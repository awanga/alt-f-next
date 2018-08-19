#!/bin/sh

# $1=dev $2=level $3=comp1 $4=comp2 $5=comp3
raid() {
	md=$1
	level=$2
	pair1=/dev/$3
	pair2=$4
	pair3=$5

	opts="--chunk=512"
	rspare=""

	case "$level" in
		linear)
			pair2="/dev/$pair2"
			ndevices=2

			if test "$pair3" != "none"; then
				pair3="/dev/$pair3"
				ndevices=3
			else
				pair3=""
			fi
			;;

		raid0)
			pair2="/dev/$pair2"
			pair3=""
			ndevices=2
			;;

		raid1)
			opts="$opts --bitmap=internal"	
			if test "$pair2" = "none"; then
				pair2="missing"
			else
				pair2="/dev/$pair2"
			fi
			if test "$pair3" != "none"; then
				opts="$opts --spare-devices=1"
				pair3="/dev/$pair3"
			else
				pair3=""
			fi
			
			ndevices=2
			;;

		raid5)
			pair2="/dev/$pair2"
			if test "$pair3" = "none"; then
				pair3="missing"
			else
				pair3="/dev/$pair3"
			fi
			opts="$opts --bitmap=internal"
			ndevices=3
			;;

	esac

	for i in $pair1 $pair2 $pair3; do
		part=$(basename $i)
		if find /sys/block/md*/slaves/$part >& /dev/null ; then
			msg "$part is currently in use by another RAID array.\n\
Either choose another componente\n\
or destroy the RAID array where $part bellongs and retry."
		fi
		if grep -q $i /proc/mounts; then
			msg "$part is currently mounted.\n\
Unmount it first, and retry.\n\
The data it contains might be lost."
			#lumount $i "creating RAID"
			#sed -i '\|^'$i'|d' $CONFT
		fi

		if test $i = "missing"; then continue; fi
		j=$(basename $i)
		k=${j:0:3}
	done

	res=$(mdadm --create /dev/$md --run --level=$level --metadata=1.0 $opts \
		--raid-devices=$ndevices $pair1 $pair2 $pair3 2>&1)
	if test $? != 0; then
		msg "Creating RAID on $md failed:\n\nError $?: $res"
	fi

	mdadm --examine --scan --config=partitions > /etc/mdadm.conf
	echo "DEVICES /dev/sd*" >> /etc/mdadm.conf
	blkid -g >& /dev/null
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

. common.sh

check_cookie
read_args
		    
#debug

CONFT=/etc/misc.conf

if test -n "$Create_bitmap"; then
	mdev=$Create_bitmap
	mdadm --grow --bitmap=internal /dev/$mdev

elif test -n "$Remove_bitmap"; then
	mdev=$Remove_bitmap
	mdadm --grow --bitmap=none /dev/$mdev

elif test -n "$Verify"; then
	mdev=$Verify
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
		lumount $mdev "Stoping RAID $mdev"
	fi
 
	res="$(mdadm --stop /dev/$mdev 2>&1)"
	if test $? != 0; then
		msg "Stopping the $mdev RAID device failed:\n\n$res"
	fi

elif test -n "$Start"; then
	mdev=$Start
	if grep -q '^'$mdev'.*inactive' /proc/mdstat ; then
		mdadm --stop /dev/$mdev > /dev/null 2>&1
	fi
	res="$(mdadm --assemble /dev/$mdev 2>&1)"
	if test $? != 0; then
		msg "Starting the $mdev RAID device failed:\n\n$res"
	fi

elif test -n "$Enlarge_raid"; then
	mdev=$Enlarge_raid
	if ismount $mdev; then
		lumount $mdev "enlarging RAID"
	fi
	if test "$(cat /sys/block/$mdev/md/bitmap/location)" != "none"; then
		had_bitmap="true"
		mdadm --grow --bitmap=none /dev/$mdev  >& /dev/null
	fi

	res="$(mdadm --grow --size=max /dev/$mdev 2>&1)"
	st=$?

	if test -n "$had_bitmap"; then
		mdadm --grow --bitmap=internal /dev/$mdev >& /dev/null
	fi

	if test $st != 0; then
		msg "Enlarging the $mdev RAID device failed:\n\n$res"
	fi

elif test -n "$Shrink_raid"; then
	mdev=$Shrink_raid

	chunk=$(cat /sys/block/$mdev/md/chunk_size)
	if test "$chunk" = 0; then chunk=65536; fi

	if ! ismount $mdev; then
		lmount $mdev "RAID Shrinking"
	fi
	eval $(df -k /dev/$mdev | awk '/'$mdev'/{
		chk='$chunk' / 1024; nsz = int (($2 * 1.1 + 128) / chk) * chk 
		printf "nsz=%d", nsz}')
	if ismount $mdev; then
		lumount $mdev "RAID Shrinking"
	fi
	
	if test "$(cat /sys/block/$mdev/md/bitmap/location)" != "none"; then
		had_bitmap="true"
		mdadm --grow --bitmap=none /dev/$mdev >& /dev/null
	fi

	res="$(mdadm --grow --size=$nsz /dev/$mdev 2>&1)"
	st=$?

	if test -n "$had_bitmap"; then
		mdadm --grow --bitmap=internal /dev/$mdev >& /dev/null
	fi

	if test $st != 0; then
		msg "Shrinking the $mdev RAID device failed:\n\n$res"
	fi

# FIXME: can't destroy raid0/linear (no menu entry). This also applies to shrink, enlarge...
# FIXME: this only works if array is started.
elif test -n "$Destroy_raid"; then
	mdev=$Destroy_raid
	lumount $mdev "destroying"
	comp=$(ls /sys/block/$mdev/slaves/)
	mdadm --stop /dev/$mdev >& /dev/null
	for i in $comp; do
		mdadm --zero-superblock /dev/$i >& /dev/null
	done
	sleep 3
	rm /dev/$mdev >& /dev/null
	mdadm --examine --scan --config=partitions > /etc/mdadm.conf
	echo "DEVICES /dev/sd*" >> /etc/mdadm.conf

elif test -n "$Details"; then
	mdev=$Details
	res=$(mdadm --detail /dev/$mdev; echo -e "\n/proc/mdstat:"; cat /proc/mdstat 2>&1)
	html_header "$mdev RAID Details"
	echo "<pre>$res</pre>$(back_button)</body></html>"
	exit 0

elif test -n "$Add_part"; then
	mdev="$Add_part"
	rdev=$(eval echo \$rdev_$mdev)
	res="$(mdadm /dev/$mdev --add /dev/$rdev 2>&1)"
	if test $? != 0; then
		msg "Adding the $rdev partition to the $mdev RAID device failed:\n\n$res"
	fi
	
elif test -n "$Remove_part"; then
	mdev="$Remove_part"
	rdev=$(eval echo \$rdev_$mdev)
	res="$(mdadm /dev/$mdev --remove /dev/$rdev 2>&1)"
	if test $? != 0; then
		msg "Removing the $rdev partition from the $mdev RAID device failed:\n\n$res"
	fi

elif test -n "$Fail_part"; then
	mdev="$Fail_part"
	rdev=$(eval echo \$rdev_$mdev)
	res="$(mdadm /dev/$mdev --fail /dev/$rdev 2>&1)"
	if test $? != 0; then
		msg "Marking failed the $rdev partition of the $mdev RAID device failed:\n\n$res"
	fi

elif test -n "$Examine_part"; then
	mdev="$Examine_part"
	rdev=$(eval echo \$rdev_$mdev)
	res=$(mdadm --examine /dev/$rdev 2>&1)
	html_header "$rdev RAID Component Details"
	echo "<pre>$res</pre>$(back_button)</body></html>"
	exit 0

elif test -n "$Clear_part"; then
	mdev="$Clear_part"
	rdev=$(eval echo \$rdev_$mdev)
	res="$(mdadm --zero-superblock /dev/$rdev 2>&1)"
	if test -n "$res"; then # no error status
		msg "Removing the superblock from the $rdev partition failed:\n\n$res"
	fi

elif test -n "$Create"; then
	raid $Create $level $comp1 $comp2 $comp3
fi

#enddebug
gotopage /cgi-bin/raid.cgi

