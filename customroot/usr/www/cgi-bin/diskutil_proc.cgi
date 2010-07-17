#!/bin/sh

tune() {
	eval $1
	shift
	eval $2

	while read ln; do
		eval $(echo $ln | awk '/^(\/dev\/sd[a-z]|\/dev\/md[0-9])/{printf "part=%s;type=%s", $1, $3}')
		if test "$type" = "ext2" -o "$type" = "ext3" -o "$type" = "ext4"; then
			tune2fs -c $mounts -i $days $part >& /dev/null
			mounts=$((mounts - 2)) # try to avoid simultaneus fsck at mount time
			days=$((days - 2))
		    fi
	done < /proc/mounts
} 

prog() {
	local dsk tmout
	dsk=/dev/"$1"
	tmout="$2"

	if ! test -b $dsk; then
		return
	fi

	#res=$(hdparm -C $dsk | awk '/drive/{print $4}') >/dev/null 2>&1
	res="$(eval echo \$power_mode_$1)"
	if test "$res" != "standby"; then	
		if test "$tmout" -eq "0"; then
			val=0;
		elif test "$tmout" -le "20"; then
			val=$((tmout * 60 / 5));
		elif test "$tmout" -le "300"; then
			val=$((240 + tmout / 30));
		fi

		/sbin/hdparm -S $val $dsk >/dev/null 2>&1
	fi 	
}

sleepnow() {
	local dsk
	dsk=/dev/$1

	if ! test -b $dsk; then
		return
	fi

	#res=$(hdparm -C $dsk | awk '/drive/{print $4}') >/dev/null 2>&1
	res="$(eval echo \$power_mode_$1)"
	if test "$res" != "standby"; then	
		/sbin/hdparm -y $dsk >/dev/null 2>&1
	fi
}


health() {
	local dsk
	dsk=/dev/$1

	if ! test -b $dsk; then
		return
	fi

	res=$(smartctl -H -i -A -l error -l selftest $dsk)
	html_header
	echo "<pre><small>"
	echo "$res"
	echo  "</small></pre><form action=\"/cgi-bin/diskutil.cgi\">
	<input type=submit value=\"Continue\"></form></html></body>"
}

bay_eject() {
	local bay dsk
	dsk=$1

	bay=$(awk '/'$dsk'/{print $1}' $CONFB)

	if ! test -b "/dev/$dsk"; then
		msg "No valid $dsk disk in $bay bay"
        elif test -z "$(cat /proc/mounts | grep /dev/$dsk)" -a \
                -z "$(cat /proc/swaps | grep /dev/$dsk)"; then
                msg "Disk $dsk in $bay bay is not in use, you can safely remove or eject it"
        else
		eject $dsk >/dev/null
		if test $? = 0; then
			msg "You can now remove or eject the $bay device"
		else
			msg "Eject fail, some programs are using the $bay device"
		fi
	fi
}

ismount() {
	if grep -q ^/dev/$1 /proc/mounts; then
		return 0
	fi
	return 1
}

# lumount part msg
lumount() {
	if ismount $1; then
		cd /dev
		ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
		if test $? != 0; then
			msg "Couldn't unmount /dev/$1 for $2 it, stop services first."
		fi
	fi
}

# lmount part msg
lmount() {
	if ! ismount $1; then
		if isdirty $part; then
			msg "Filesystem $part is dirty, clean it before mounting."
		fi

		cd /dev
		ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
		if test $? != 0; then
			msg "Couldn't mount /dev/$1 for $2 it."
		fi
	fi
}

# clean %1=part %2=type $3=name
clean() {

	case $2 in
		ext2|ext3|ext4) opts="-fpD" ;;
		vfat) opts="-a" ;;
		ntfs) opts="" ;;
		*) 	opts="" ;;
	esac

	cat<<-EOF > /tmp/$3-$1
		#!/bin/sh
		echo \$$ > \$0.pid
		logger "\$(fsck $opts /dev/$1 2>&1)"
		st=\$?
		if test "\$st" = 0 -o "\$st" = 1; then
			logger "Cleaned /dev/$1 OK"
			cd /dev
			ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
		fi
		logger "Cleaning /dev/$1 failed with error code \$st"
	EOF

	chmod +x /tmp/$3-$1
	/tmp/$3-$1 < /dev/console > /dev/null 2> /dev/null &
}

# format $1=part $2=type $3=label
format() {

	case $2 in
		ext2|ext3|ext4) opts=""; id=83 ;;
		vfat) opts="-v"; id=c ;; # c Win95 FAT32 (LBA)
		ntfs) opts="-f"; id=7 ;; # 7 HPFS/NTFS
		*) msg "Wrong filesystem type." ;;
	esac

	cat<<-EOF > /tmp/format-$1
		#!/bin/sh
		echo \$$ > \$0.pid
		logger "\$(eval mkfs.$2 $opts /dev/$1 2>&1)"
		st=\$?
		if test \$st != 0; then
			logger "Formating /dev/$1 with $2 failed with code \$st"
			exit 1
		fi
		logger "Formated /dev/$1 with $2 OK"

		if test -n "$3"; then
			plabel $1 "$3" 
		fi

		if test "${1:0:2}" = "sd"; then
			p=${1:0:3}
			pn=${1:3}
			if test "\$pn" -ge 1 -a "\$pn" -le 4; then
				sfdisk --change-id /dev/\$p \$pn $id -O /tmp/mbr-\$p
				if test \$? != 0; then
					sfdisk /dev/\$p -I /tmp/mbr-\$p
				fi
				rm /tmp/mbr-\$p
			fi
		fi

		cd /dev
		ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
	EOF

	chmod +x /tmp/format-$1
	/tmp/format-$1 < /dev/console > /dev/null 2> /dev/null &
}

. common.sh

check_cookie
read_args
		    
#debug

CONFF=/etc/hdsleep.conf
CONFT=/etc/tune.conf
CONFB=/etc/bay
CONFTB=/etc/fstab

. /tmp/power_mode

if test "$Submit" = "standby"; then
	while read ln; do
		eval $(echo $ln | awk '/sd[a-z]/{printf "bay=%s;dsk=%s", $1, $2}')
		eval tmout=\$$bay
		sed -i '/^'$bay'/d' $CONFF
		echo "$bay $tmout" >> $CONFF
		prog $dsk $tmout
	done < $CONFB

elif test "$Submit" = "tune"; then
	arg=""
	for i in days mounts; do
		eval val=\$$i
		sed -i '/^'$i'/d' $CONFT
		echo "$i $val" >> $CONFT
		arg="$arg $i=$val"
	done
	tune $arg
  
elif test -n "$StandbyNow"; then
	sleepnow $StandbyNow
	
elif test -n "$Eject"; then
	bay_eject $Eject

elif test -n "$Status"; then
	health $Status
	exit

elif test -n "$setLabel"; then
	part=$setLabel
	eval lab=\$lab_$part
	lab=$(httpd -d $lab)

	lumount $part
	plabel $part "$lab"
	lmount $part

elif test -n "$Mount"; then
	part=$Mount
	lmount $part "mount"

elif test -n "$unMount"; then
	part=$unMount
	lumount $part "unmount"

elif test -n "$Clean"; then
	part=$Clean
	type=$(blkid -s TYPE -o value /dev/$part)
	lumount $part "cleaning"
	clean $part $type "clean"
		
elif test -n "$Format"; then
	part=$Format
	label="$(plabel $part)"
	eval type=\$type_$part
	lumount $part "formating"
	format $part $type "$label"

elif test -n "$Convert"; then
	part=$Convert
	eval type=\$type_$part
	from=$(blkid -s TYPE -o value /dev/$part)
	lumount $part "converting"

	if test "$type" != "ext3" -a "$type" != "ext4"; then
		msg "Can only convert upward from 'ext' filesystems."
	fi 

	if test $from = "ext2"; then # 2->3	
		logger "$(tune2fs -j /dev/$part 2>&1)"
	fi

	if test $type = "ext4"; then # 3->4
		logger "$(tune2fs -O extents,uninit_bg,dir_index /dev/$part 2>&1)"
	fi

	clean $part $from "convert"

elif test -n "$Create"; then
	mdev=$Create
	mdadm --grow --bitmap=internal /dev/$mdev

elif test -n "$Remove"; then
	mdev=$Remove
	mdadm --grow --bitmap=none /dev/$mdev

elif test -n "$Check"; then
	mdev=$Check
	echo "check" > /sys/block/$mdev/md/sync_action

elif test -n "$Repair"; then
	mdev=$Repair
	echo "repair" > /sys/block/$mdev/md/sync_action

elif test -n "$Abort"; then
	mdev=$Abort
	echo "idle" > /sys/block/$mdev/md/sync_action

elif test -n "$Stop"; then
	mdev=$Stop
	if grep -q ^/dev/$mdev /proc/mounts ; then
		lumount $mdev "stoping RAID $mdev"
	fi
 
	res=$(mdadm --stop /dev/$mdev 2>&1)
	if test $? != 0; then
		msg "$res"
	fi

elif test -n "$Start"; then
	mdev=$Start
	res=$(mdadm --assemble /dev/$mdev 2>&1)
	if test $? != 0; then
		msg "$res"
	fi

elif test -n "$Grow"; then
	mdev=$Grow

	mdadm --grow --bitmap=none /dev/$mdev 2>&1 /dev/null
	res=$(mdadm --grow /dev/$mdev --size=max 2>&1)
	if test $? != 0; then
		msg "$res"
	fi

elif test -n "$Apply"; then
	mdev=$Apply
	if test "$rops" = "none" -o "$rdev" = "none"; then
		msg "You must specify a partition and an operation"
	fi

	case $rops in
		add) res="$(mdadm /dev/$mdev --add /dev/$rdev 2>&1)" ;;
		remove) res="$(mdadm /dev/$mdev --fail /dev/$rdev --remove /dev/$rdev 2>&1)" ;;
	esac

	if test $? != 0; then
		msg "$res"
	fi
else
	debug
fi

#enddebug
gotopage /cgi-bin/diskutil.cgi

