#!/bin/sh

# $1=days $2=mounts
tune() {
	local days mounts
	days=$1
	mounts=$2
	while read ln; do
		eval $(echo $ln | awk '/^(\/dev\/sd[a-z]|\/dev\/md[0-9])/{printf "part=%s;type=%s", $1, $3}')
		if test "$type" = "ext2" -o "$type" = "ext3" -o "$type" = "ext4"; then
			tune2fs -c $mounts -i $days $part >& /dev/null
			mounts=$((mounts - 2)) # try to avoid simultaneus fsck at mount time
			days=$((days - 2))
		    fi
	done < /proc/mounts
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
		trap "" 1
		echo \$$ > \$0.pid
		res="\$(fsck $opts /dev/$1 2>&1)"
		st=\$?
		if test "\$st" = 0 -o "\$st" = 1; then
			logger "Cleaned /dev/$1 OK"
			cd /dev
			ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
			exit 0
		fi
		logger "Cleaning /dev/$1 failed with error code \$st. \$res"
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
		trap "" 1
		echo \$$ > \$0.pid
		res="\$(eval mkfs.$2 $opts /dev/$1 2>&1)"
		st=\$?
		if test \$st != 0; then
			logger "Formating /dev/$1 with $2 failed with code \$st: \$res"
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

# $1=part $2=shrink|enlarg 
resize() {
	nsz=""
	if test "$2" = "shrink"; then
		if ! ismount $1; then
			lmount $1 "${2}ing"
		fi
		eval $(df -k /dev/$1 | awk '/'$1'/{printf "nsz=%dK", 1.1 * $3 }')
	fi

	if ismount $1; then
		lumount $1 "${2}ing"
	fi

	cat<<-EOF > /tmp/$2-$1
		#!/bin/sh
		trap "" 1
		echo \$$ > \$0.pid
		res="\$(fsck -fy /dev/$1 2>&1)"
		st=\$?
		if ! test "\$st" = 0 -o "\$st" = 1; then
			logger "Cleaning /dev/$1 failed with error code \$st: \$res"
			exit 1
		fi
		logger "Cleaned /dev/$1 OK"
		
		res="\$(resize2fs /dev/$1 $nsz 2>&1)"
		if test $? != 0; then
			logger "${2}ing /dev/$1 failed: $res"
			exit 1
		fi
		logger "${2}ing /dev/$1 succeeded"
	EOF

	chmod +x /tmp/$2-$1
	/tmp/$2-$1 < /dev/console > /dev/null 2> /dev/null &
}

# wipe $1=part
wipe() {
	lumount $1 "wiping"
	eval $(sfdisk -uM -l /dev/${1:0:3} | awk '/'$1'/{printf "nblk=%d", $5/1024}')
	cat<<-EOF > /tmp/wip-$1
		#!/bin/sh
		trap "" 1
		echo \$$ > \$0.pid
		res="\$(nice dd if=/dev/zero of=/dev/$1 bs=1M count=$nblk 2>&1)"
		st=\$?
		if test "\$st" = 0; then
			logger "Wiped /dev/$1 OK"
			exit 0
		fi
		logger "Wiping /dev/$1 failed with error code \$st. \$res"
	EOF

	chmod +x /tmp/wip-$1
	/tmp/wip-$1 < /dev/console > /dev/null 2> /dev/null &
}

. common.sh

check_cookie
read_args
		    
#debug

CONFB=/etc/bay
CONFTB=/etc/fstab
CONFT=/etc/misc.conf

if test "$Submit" = "tune"; then
	sed -i '/^TUNE_DAYS/d' $CONFT
	sed -i '/^TUNE_MOUNTS/d' $CONFT
	echo TUNE_DAYS=$TUNE_DAYS >> $CONFT
	echo TUNE_MOUNTS=$TUNE_MOUNTS >> $CONFT

	tune $TUNE_DAYS $TUNE_MOUNTS

elif test -n "$setLabel"; then
	part=$setLabel
	eval lab=\$lab_$part
	if test -n "$lab"; then
		lab=$(httpd -d $lab)
	fi

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
		res="$(tune2fs -j /dev/$part)"
		if test $? != 0; then
			msg "$res"
		fi
	fi

	if test $type = "ext4"; then # 3->4
		res="$(tune2fs -O extents,uninit_bg,dir_index /dev/$part)"
		if test $? != 0; then
			msg "$res"
		fi
	fi

	clean $part $from "convert"

elif test -n "$Shrink"; then
	part=$Shrink
	resize $part "shrink"

elif test -n "$Enlarge"; then
	part=$Enlarge
	resize $part "enlarg"

elif test -n "$Wipe"; then
	part=$Wipe
	wipe $part

fi

#enddebug
gotopage /cgi-bin/diskmaint.cgi

