#!/bin/sh

# $1=days $2=mounts
tune() {
	local days mounts
	days=$1
	mounts=$2
	while read ln; do
		eval $(echo $ln | awk '/^(\/dev\/sd[a-z]|\/dev\/md[0-9])/{printf "part=%s;type=%s", $1, $3}')
		if test "$type" = "ext2" -o "$type" = "ext3" -o "$type" = "ext4"; then

			cnt=$(tune2fs -l $part 2> /dev/null | awk '/^Mount count:/ {FS=":"; cnt=$2; print cnt+1}')
			if test $cnt -ge $mounts; then tuneopts="-C $mounts -T now"; fi

			tune2fs -c $mounts $tuneopts -i $days $part >& /dev/null
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
			msg "Filesystem $part is dirty, check it before mounting."
		fi

		cd /dev
		ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
		if test $? != 0; then
			msg "Couldn't mount /dev/$1 for $2 it."
		fi
	fi
}

# check $1=part $2=type $3=name
check() {
	case $2 in
		ext2|ext3|ext4) 
			if test "$3" = "fix"; then
				opts="-fyD"
			else
				opts="-fpD"
			fi
			;;
		vfat) opts="-a" ;;
		ntfs) opts="" ;;
		btrfs) 
			lmount $1
			msg "Checking or Fixing a btrfs filesystem has to be done from the command line." ;;
		*) msg "Unsuported $2 filesystem, you have to resort to the command line." ;;
	esac
	logf=/tmp/${3}-${1}.log

	cat<<-EOF > /tmp/$3-$1
		#!/bin/sh
		trap "" 1
		echo \$$ > \$0.pid
		echo heartbeat > $PLED
		mkfifo /tmp/fsck_pipe-$1 >& /dev/null
		(while true; do
			dd if=/tmp/fsck_pipe-$1 of=$logf- bs=64K count=1 2> /dev/null 
			mv $logf- $logf
			sleep 10
		done)&
		wj=\$!
		res=\$(nice fsck $opts -C5 /dev/$1 2>&1 5<> /tmp/fsck_pipe-$1)
		st=\$?
		if test -z "$(ls /tmp/check-* /tmp/convert-* 2>/dev/null)"; then echo none > $PLED; fi
		kill \$wj
		#echo > /tmp/fsck_pipe-$1
		rm \$0* /tmp/fsck_pipe-$1
		if test "\$st" = 0 -o "\$st" = 1; then
			cd /dev
			ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
			exit 0
		else
			emsg="Checking $1 finished with status code \$st: \$res"
			logger "\$emsg"
			echo "<li><pre>\$emsg</pre></li>" >> $SERRORL
		fi
	EOF

	chmod +x /tmp/$3-$1
	/tmp/$3-$1 < /dev/console > /dev/null 2> /dev/null &
}

# format $1=part $2=type $3=label
format() {
	raidopts=""
	if test -d /sys/block/${part}/md; then
		if test "$(cat /sys/block/${part}/md/array_state)" = "clear"; then
			msg "Error, RAID device $part is not active."
		fi
		level=$(cat /sys/block/${part}/md/level)
		ndisks=$(cat /sys/block/${part}/md/raid_disks)
		if test "$level" = "raid0" -o "$level" = "raid5"; then
			if test "$level" = "raid0"; then
				nd=$ndisks
			else
				nd=2 # can start in degraded, but 3 (2 of data) has to be used
			fi
			blk=4096
			chunk=$(cat /sys/block/${part}/md/chunk_size)
			stride=$((chunk / blk))
			stripew=$((stride * nd))
			raidopts="-b $blk -E stride=$stride,stripe-width=$stripew"
		fi
	fi

	case $2 in
		ext2|ext3|ext4) opts="-v -m 0 $raidopts"; id=83 ;;
		btrfs) opts="-f"; id=83 ;;
		vfat) opts="-v"; id=c ;; # c Win95 FAT32 (LBA)
		ntfs) opts="-v -f"; id=7 ;; # 7 HPFS/NTFS
		*) msg "Wrong filesystem type." ;;
	esac
	logf=/tmp/format-${1}.log

	cat<<-EOF > /tmp/format-$1
		#!/bin/sh
		trap "" 1
		echo \$$ > \$0.pid
		nice mkfs.$2 $opts /dev/$1 > $logf 2>&1
		st=\$?
		if test \$st != 0; then
			emsg="Formatting $1 with $2 failed with code \$st: \$(cat $logf)"
			logger "\$emsg"
			echo "<li><pre>\$emsg</pre></li>" >> $SERRORL
			rm \$0*
			exit 1
		fi
		if test "$2" = "ext3"; then
			tune2fs -o journal_data_ordered /dev/$1
		fi
		logger "Formated /dev/$1 with $2 OK"

		if test -n "$3"; then
			plabel $1 "$3" 
		fi

		if test "${1:0:2}" = "sd"; then
			p=${1:0:3}
			pn=${1:3}
			if ! fdisk -l /dev/\$p 2> /dev/null | grep -q "Found valid GPT"; then # non GPT disk
				if test "\$pn" -ge 1 -a "\$pn" -le 4; then
					sfdisk --change-id /dev/\$p \$pn $id -O /tmp/mbr-\$p
					if test \$? != 0; then
						sfdisk /dev/\$p -I /tmp/mbr-\$p
					fi
					rm /tmp/mbr-\$p
				fi
			fi
		fi
		rm \$0*
		cd /dev
		ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
	EOF

	chmod +x /tmp/format-$1
	/tmp/format-$1 < /dev/console > /dev/null 2> /dev/null &
}

# $1=part $2=shrink|enlarg 
resize() {
	if test $type = "btrfs"; then
		if ! ismount $1; then
			lmount $1 "${2}ing"
		fi
		mp=$(awk '/^\/dev\/'$1'[[:space:]]/{print $2}' /proc/mounts)
		nsz=max
		if test "$2" = "shrink"; then
			nsz=$(btrfs filesystem usage --raw $mp | awk '/Device allocated:/{printf "%.0f", 1.05 * $3 }')
		fi
	else
		nsz=""
		if test "$2" = "shrink"; then
			nsz="-M"
		fi
		if ismount $1; then
			lumount $1 "${2}ing"
		fi
	fi

	logf=/tmp/${2}-${1}.log

	cat<<-EOF > /tmp/$2-$1
		#!/bin/sh
		trap "" 1
		echo \$$ > \$0.pid
		echo heartbeat > $PLED
		mkfifo /tmp/fsck_pipe-$1 >& /dev/null
		(while true; do
			dd if=/tmp/fsck_pipe-$1 of=$logf- bs=64K count=1 2> /dev/null 
			mv $logf- $logf
			sleep 10
		done)&
		wj=\$!
		res=\$(nice fsck -fp -C5 /dev/$1 2>&1 5<> /tmp/fsck_pipe-$1)
		st=\$?
		kill \$wj
		#echo > /tmp/fsck_pipe-$1 # dd might be blocked
		rm /tmp/fsck_pipe-$1
		if test -z "$(ls /tmp/check-* /tmp/convert-* 2>/dev/null)"; then echo none > $PLED; fi

		if ! test "\$st" = 0 -o "\$st" = 1; then
			emsg="Checking $1 failed with error code \$st: \$res"
			logger "\$emsg"
			echo "<li><pre>\$emsg</pre></li>" >> $SERRORL
			rm \$0*
			exit 1
		fi
		logger "Checking /dev/$1 OK"
		
		if test $type = btrfs; then
			nice btrfs filesystem resize $nsz $mp > $logf 2>&1
		else
			nice resize2fs -p /dev/$1 $nsz > $logf 2>&1
		fi
		if test $? != 0; then
			emsg="${2}ing $1 failed: \$(cat $logf)"
			logger "\$emsg"
			echo "<li><pre>\$emsg</pre></li>" >> $SERRORL
			rm \$0*
			exit 1
		fi
		logger "${2}ing /dev/$1 succeeded"
		rm \$0*
		cd /dev
		ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
	EOF

	chmod +x /tmp/$2-$1
	/tmp/$2-$1 < /dev/console > /dev/null 2> /dev/null &
}

# wipe $1=part
wipe() {
	lumount $1 "wiping"

	if test -f  /sys/block/$1/size; then
 		devf=/sys/block/$1/size
	elif test -f /sys/block/${1:0:3}/$1/size; then
		devf=/sys/block/${1:0:3}/$1/size
	else
		msg "Can't find device $1 size."
	fi

	nsize=$(expr $(cat $devf)  \* 512)
	nblk=$(expr $nsize / 4194304)
	
	cat<<-EOF > /tmp/wip-$1
		#!/bin/sh
		trap "" 1
		echo $nsize > /tmp/wip-$1.log
		nice dd if=/dev/zero of=/dev/$1 bs=4M count=$nblk 2>> /tmp/wip-$1.log &
		echo \$! > \$0.pid
		wait
		st=\$?
		if test "\$st" = 0; then
			logger "Wiped /dev/$1 OK"
			rm \$0*
			exit 0
		fi
		emsg="Wiping $1 failed with error code \$st: \$(tail /tmp/wip-$1.log)"
		logger "\$emsg"
		echo "<li><pre>\$emsg</pre></li>" >> $SERRORL
		rm \$0*
	EOF

	chmod +x /tmp/wip-$1
	/tmp/wip-$1 < /dev/console > /dev/null 2> /dev/null &
}

# $1-part $2-from $3-to
convert() {
	html_header "Converting filesystem on $1"
	busy_cursor_start
	if test "$2" = "ext2"; then # 2->3, perhaps intermediate step	
		echo "<p>Converting from ext2 to ext3..."
		res="$(tune2fs -j /dev/$1)"
		if test $? != 0; then
			echo "failed: <pre>$res</pre></p>$(back_button)"
		else
			echo "OK</p>"
		fi
	fi

	if test "$2" = "ext2" -a "$3" = "ext3"; then # 2->3, final
		echo "<p>Finish converting to ext3..."
		res="$(tune2fs -m 0 -o journal_data_ordered /dev/$1)"
		if test $? != 0; then
			echo "failed: <pre>$res</pre></p>$(back_button)"
		else
			echo "OK</p>"
		fi
	elif test "$3" = "ext4"; then # 3->4, final
		echo "<p>Converting from ext3 to ext4..."
		res="$(tune2fs -m 0 -O extents,uninit_bg,dir_index /dev/$1)"
		if test $? != 0; then
			echo "failed: <pre>$res</pre></p>$(back_button)"
		else
			echo "OK</p>"
		fi
	fi
	busy_cursor_end
}

. common.sh

check_cookie
read_args

#debug
#set -x

CONFT=/etc/misc.conf
SERRORL=/var/log/systemerror.log
PLED=/tmp/sys/power_led/trigger

if test "$Submit" = "tune"; then
	sed -i '/^TUNE_DAYS/d' $CONFT
	sed -i '/^TUNE_MOUNTS/d' $CONFT
	echo TUNE_DAYS=$TUNE_DAYS >> $CONFT
	echo TUNE_MOUNTS=$TUNE_MOUNTS >> $CONFT

	tune $TUNE_DAYS $TUNE_MOUNTS

elif test -n "$setLabel"; then
	eval part=\$part_$setLabel
	eval lab=\$lab_$setLabel
	if test -n "$lab"; then
		lab=$(httpd -d $lab)
	fi

	lumount $part
	plabel $part "$lab"
	lmount $part

elif test -n "$setMountOpts"; then
	eval part=\$part_$setMountOpts
	eval mopts=\$mopts_$setMountOpts

	if test -n "$mopts"; then
		mopts=$(httpd -d $mopts)
	fi

	# FIXME: if fs is mounted, use 'remount' mount option instead, as fs might be busy
	lumount "$part"

	TF=$(mktemp -t) 
	awk '{
		if ($1 == "/dev/'$part'") {
			$4 = "'$mopts'"
			printf "%s\n", $0
		} else {
			print $0
		}
	}' /etc/fstab > $TF
	mv $TF /etc/fstab

	uuid=$(blkid -o value -c /dev/null -s UUID /dev/$part | tr '-' '_')
	sed -i '/^mopts_'${uuid}'=/d' /etc/misc.conf

	if test "$mopts" != "defaults"; then
		echo "mopts_${uuid}=$mopts" >> /etc/misc.conf
	fi
	
	lmount "$part"

elif test -n "$Mount"; then
	eval part=\$part_$Mount
	lmount "$part" "mount"

elif test -n "$unMount"; then
	eval part=\$part_$unMount
	lumount "$part" "unmount"

elif test -n "$Check"; then
	eval part=\$part_$Check
	type=$(blkid -s TYPE -o value /dev/$part)
	lumount "$part" "checking"
	check "$part" "$type" "check"

elif test -n "$ForceFix"; then
	eval part=\$part_$ForceFix
	type=$(blkid -s TYPE -o value /dev/$part)
	lumount "$part" "fixing"
	check "$part" "$type" "fix"
		
elif test -n "$Format"; then
	eval part=\$part_$Format
	eval type=\$type_$Format
	label="$(plabel $part)"
	lumount "$part" "formatting"
	format "$part" "$type" "$label"

elif test -n "$Details"; then
    eval part=\$part_$Details
    res=$(tune2fs -l "/dev/$part" 2>&1)
    html_header "$part Filesystem Details"
    echo "<pre>$res</pre>$(back_button)</body></html>"
    exit 0

elif test -n "$Convert"; then
	eval part=\$part_$Convert
	eval type=\$type_$Convert

	if test "$type" != "ext3" -a "$type" != "ext4"; then
		msg "Can only convert upward from 'ext' filesystems."
	fi
	
	from=$(blkid -s TYPE -o value /dev/$part)
	lumount "$part" "converting"

	convert "$part" "$from" "$type"
	check "$part" "$from" "check"
	js_gotopage /cgi-bin/diskmaint.cgi

elif test -n "$Shrink"; then
	eval part=\$part_$Shrink
	type=$(blkid -s TYPE -o value /dev/$part)
	resize "$part" "shrink"

elif test -n "$Enlarge"; then
	eval part=\$part_$Enlarge
	type=$(blkid -s TYPE -o value /dev/$part)
	resize "$part" "enlarg"

elif test -n "$Wipe"; then
	eval part=\$part_$Wipe
	wipe "$part"

fi

#enddebug
gotopage /cgi-bin/diskmaint.cgi

