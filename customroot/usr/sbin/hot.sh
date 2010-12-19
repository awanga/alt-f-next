#!/bin/sh

debug=true
maxsize=32768 # bytes

if test -n "$debug"; then
	if test "$(stat -t /var/log/hot.log 2>/dev/null | cut -d" " -f2)" -gt $maxsize; then
		tf=$(mktemp -t)
		mv /var/log/hot.log $tf
		tail -n $(expr $maxsize / 26) $tf > /var/log/hot.log
		rm $tf
	fi
	exec >> /var/log/hot.log 2>&1
	set -x
	echo "DATE=$(date)"
	env	
fi

if test -z "$ACTION"; then echo "NO ACTION"; return; fi

# arghhh... using non-partitioned MD.
# an MD can be partitioned, thus the kernel sends the /dev/md? event as being
# a disk. But we use disk-based partitioning, thus a /dev/md? is in reality
# a partition. This might cause problems if plugging a MD-based partitioned disk
if test ${MDEV%%[0-9]} = "md" -a -z "$PHYSDEVDRIVER" -a \
	-z "$PHYSDEVPATH" -a -z "$PHYSDEVBUS" -a "$DEVTYPE" = "disk"; then
	echo "md: changing DEVTYPE from disk to partition"
	DEVTYPE="partition"
fi

if test "$ACTION" = "add" -a "$DEVTYPE" = "partition"; then
	if test -z "$MDEV"; then exit 0; fi

	res=$(mdadm --query --examine --export --test $PWD/$MDEV)
	if test $? = 0; then
		#if ! test -f /etc/mdadm.conf; then
			mdadm --examine --scan > /etc/mdadm.conf
			#echo "DEVICE /dev/sd*" >> /etc/mdadm.conf
		#fi                                                            
		#mdadm --incremental --run $PWD/$MDEV
		mdadm --incremental --no-degraded $PWD/$MDEV
		eval $res
		if test -z "$MD_NAME"; then # version 0.9 doesnt have the MD_NAME attribute
			MD_NAME=$(ls /sys/block/${MDEV:0:3}/$MDEV/holders/)
			MD_NAME=${MD_NAME:2}
		else
			MD_NAME=${MD_NAME##*:} # remove host: part
		fi
		if test -e $PWD/md$MD_NAME -a -b $PWD/md$MD_NAME; then
			mdadm --query --detail $PWD/md$MD_NAME
			# this is needed to generate a *new* md? event when the 2nd/3d disk is inserted. It mounts the device as soon as possible. It has the inconvenient that when the 2nd disk is added it is rsynced. For linear and raid 0 this is fine, but not for raid1 or 5. FIXME
			if test $? = 0; then # generate hotplug event for /dev/md?. 
#				echo "add" > /sys/block/md$MD_NAME/uevent
				(cd /dev && ACTION=add DEVTYPE=partition PWD=/dev MDEV=md$MD_NAME /usr/sbin/hot.sh)
			fi
		fi
		return 0
	fi

	fstype=$(blkid -s TYPE -o value -w /dev/null -c /dev/null $PWD/$MDEV)
	fsckcmd="fsck"
	case $fstype in
		ext2|ext3|ext4)	fsopt="-p" ;;
		iso9660) fsckcmd="echo" ;;
		vfat) fsopt="-a" ;;			
		ntfs)
			if ! test -f /usr/bin/ntfsfix; then fsckcmd="echo "; fi
			fstype="ntfs-3g"
			fsopt=""
			;; 
		swap)
			swapon -p 1 $PWD/$MDEV
			mount -o remount,size=64M /tmp
			sed -i '\|^'$PWD/$MDEV'|d' /etc/fstab
			echo "$PWD/$MDEV none swap pri=1 0 0" >> /etc/fstab
			return 0
			;;
		*)
			logger "hot: unknown partition type \"$fstype\" in \"$MDEV\""
			return 0
			;;
	esac

	lbl=$(blkid -s LABEL -o value -w /dev/null -c /dev/null $PWD/$MDEV | tr ' ' '_')
#	if test -z "$lbl" -o -d /mnt/$lbl; then lbl=$MDEV; fi # FIXME handle duplicate labels
	if test -z "$lbl"; then lbl=$MDEV; fi
	/bin/mkdir /mnt/$lbl
	if mountpoint /mnt/$lbl; then exit 0; fi

	echo heartbeat > "/sys/class/leds/power:blue/trigger"
	res="$($fsckcmd $fsopt $PWD/$MDEV 2>&1)"
	if test $? -ge 2; then fsflg="-o ro"; fi
	logger "$res"
	echo none > "/sys/class/leds/power:blue/trigger"
	/bin/mount -t $fstype $fsflg $PWD/$MDEV /mnt/$lbl
	sed -i '\|^'$PWD/$MDEV'|d' /etc/fstab
	echo "$PWD/$MDEV /mnt/$lbl $fstype defaults 0 0" >> /etc/fstab

	if test -d "/mnt/$lbl/Users"; then
		if ! test -h /home -a -d "$(readlink -f /home)" ; then
			ln -s "/mnt/$lbl/Users" /home
		fi
	fi

	if test -d "/mnt/$lbl/Public"; then
		if ! test -h /Public -a -d "$(readlink -f /Public)" ; then
			ln -s "/mnt/$lbl/Public" /Public
		fi
	fi

	if test -d "/mnt/$lbl/Backup"; then
		if ! test -h /Backup -a -d "$(readlink -f /Backup)" ; then
			ln -s "/mnt/$lbl/Backup" /Backup
		fi
	fi

	if test -d "/mnt/$lbl/ffp"; then
		if ! test -h /ffp -a -d "$(readlink -f /ffp)" ; then
			ln -s "/mnt/$lbl/ffp" /ffp
			if test $? = 0 -a -x /etc/init.d/S??ffp; then
					/etc/init.d/S??ffp start
			fi
		fi
	fi

	if test -d /mnt/$lbl/Alt-F; then
		if ! test -h /Alt-F -a -d "$(readlink -f /Alt-F)"; then
			rm -f /mnt/$lbl/Alt-F/Alt-F /mnt/$lbl/Alt-F/ffp /mnt/$lbl/Alt-F/home
			ln -s /mnt/$lbl/Alt-F /Alt-F
			echo "DONT'T ADD, REMOVE OR CHANGE ANY FILE ON THIS DIRECTORY
OR IN ANY OF ITS SUBDIRECTORIES, OR THE SYSTEM MIGHT HANG." > /Alt-F/README.txt
			for i in /Alt-F/etc/init.d/S??*; do
				f=$(basename $i)
				ln -sf /usr/sbin/rcscript /sbin/rc${f#S??}
			done
			loadsave_settings -ta
			mount -t aufs -o remount,prepend:/mnt/$lbl/Alt-F=rw /
		fi
	fi


elif test "$ACTION" = "add" -a "$DEVTYPE" = "disk"; then

	if test -d /sys/block/$MDEV/md; then # md disk
		echo $MDEV: NO PARTITION BASED MD

	else # "normal" disk (not md)

		# which bay?	
		# dont use PHYSDEVPATH, for easy mounting disks in /etc/init.d/rcS 
		PHYSD=$(readlink /sys/block/$MDEV/device) 
		if $(echo $PHYSD | grep -q /host0/); then
			bay="right"
		elif $(echo $PHYSD | grep -q /host1/); then
			bay="left"
		elif $(echo $PHYSD | grep -q /usb1/); then
			bay="usb"${MDEV:2}
		fi
	
		if test -n "$bay"; then
			sed -i '/^'$bay'_/d' /etc/bay
			sed -i '/^'$MDEV'/d' /etc/bay

			eval $(smartctl -i $PWD/$MDEV | awk '
				/^Model Family/ {printf "fam=\"%s\";", substr($0, index($0,$3))}
				/^Device Model/ {printf "mod=\"%s\";", substr($0, index($0,$3))}
				/^SMART support is:.*Enabled/ {print "smart=yes;"}')

			if test -z "$smart"; then
				fam="$(cat /sys/block/$MDEV/device/vendor)"
				mod="$(cat /sys/block/$MDEV/device/model)"
			fi
			cap="$(awk '{printf "%.1f GB", $0 * 512 / 1e9}' /sys/block/$MDEV/size)"
			echo ${bay}_dev=$MDEV >> /etc/bay
			echo $MDEV=${bay} >> /etc/bay
			echo ${bay}_cap=\"$cap\" >> /etc/bay
			echo ${bay}_fam=\"$fam\" >> /etc/bay
			echo ${bay}_mod=\"$mod\" >> /etc/bay

			if test -f /etc/misc.conf; then
				. /etc/misc.conf

				# set advanced power management
				eval pm=$(echo \$HDPOWER_$bay | tr 'a-z' 'A-Z' )
				if test -n "$pm"; then
					hdparm -B $pm $PWD/$MDEV
				fi

				# set disk spin down
				eval tm=$(echo \$HDSLEEP_$bay | tr 'a-z' 'A-Z' )
				if test -n "$tm"; then
		
					if test "$tm" -le "20"; then
						val=$((tm * 60 / 5))
					elif test "$tm" -le "300"; then
						val=$((240 + tm / 30))
					fi
					hdparm -S $val $PWD/$MDEV
				fi

				if rcsmart status; then
					rcsmart reload
				fi
			fi
		fi

		# no low latency (server, not desktop)
		echo 0 > /sys/block/$MDEV/queue/iosched/low_latency
	
		# for now use only disk partition-based md
		if ! sfdisk -l /dev/sdb | awk '$6 == "da" || $6 == "fd" { exit 1 }'; then
			mdadm --examine --scan > /etc/mdadm.conf
		fi
	fi

elif test "$ACTION" = "remove" -a "$DEVTYPE" = "disk"; then

	mdadm --examine --scan > /etc/mdadm.conf
	blkid -g

	# remove some modules (repeat it while there are some?)
	lsmod | awk '{if ($3 == 0) system("modprobe -r " $1)}'

	. /etc/bay
	bay=$(eval echo \$$MDEV)
	if test -n "$bay"; then
		sed -i '/^'$bay'_/d' /etc/bay
		sed -i '/^'$MDEV'/d' /etc/bay
	fi

	if rcsmart status >& /dev/null; then
		rcsmart reload
	fi

elif test "$ACTION" = "remove" -a "$DEVTYPE" = "partition"; then

	ret=0
	mdadm --examine --scan > /etc/mdadm.conf

	mpt=$(awk '/'$MDEV'/{print $2}' /proc/mounts )
	if $(grep -q -e ^$PWD/$MDEV /proc/swaps); then
		swapoff $PWD/$MDEV
		ret=$?
		if test $(awk '/SwapTotal/ {print $2}' /proc/meminfo) = "0"; then
			mount -o remount,size=32M /tmp
		fi
	elif $(grep -q -e ^$PWD/$MDEV /proc/mounts); then
		if test "$(readlink -f /ffp)" = "$mpt/ffp"; then
			if test -x /etc/init.d/S??ffp; then
				/etc/init.d/S??ffp stop
			fi
			rm -f /ffp
		fi

		if test "$(readlink -f /home)" = "$mpt/Users"; then
			rm -f /home
		fi

		if test "$(readlink -f /Public)" = "$mpt/Public"; then
			rm -f /Public
		fi

		if test "$(readlink -f /Backup)" = "$mpt/Backup"; then
			rm -f /Backup
		fi

 		if test "$(readlink -f /Alt-F)" = "$mpt/Alt-F"; then
 			mount -t aufs -o remount,del:$mpt/Alt-F /
			if test $? = "0"; then
				loadsave_settings -fa
				rm -f /Alt-F
				rm -f /$mpt/Alt-F//README.txt
			else
				exit 1	# busy?
			fi
 		fi
		# umount $PWD/$MDEV
		umount $mpt
		ret=$?
		if test "$ret" = "0"; then
			rmdir $mpt
		else
			umount -r $mpt # damage control
		#	ret=$?	# "eject" should fail.
		fi
	elif test -e /proc/mdstat -a -n "$(grep $MDEV /proc/mdstat)"; then
		eval $(mdadm --examine --export $PWD/$MDEV)
		#md=md${MD_NAME##*:} # remove host: part # 1.x metadata (could use /sys/...holders)
		#if test -z "$md"; then
			md=$(ls /sys/block/${MDEV%%[0-9]}/$MDEV/holders) # 0.9 metadata
		#fi
		type=$MD_LEVEL
		if test -n "$md" -a -b $PWD/$md ; then
			act=$(cat /sys/block/$md/md/array_state)
			eval $(mdadm --detail $PWD/$md | awk \
				'/Active Devices/{ printf "actdev=%s;", $4}
				/Working Devices/{ printf "workdev=%s;", $4}')
			if test "$actdev" = 2; then # FIXME
				other=$(ls /sys/block/$md/slaves/ | grep -v $MDEV)
			fi
			if test "$act" != "inactive" -a \( \
				\( "$type" = "raid1" -a "$actdev" = 2 \) -o \
				\( "$type" = "raid5" -a "$actdev" = 3 \) \) ; then
				mdadm $PWD/$md --fail $PWD/$MDEV --remove $PWD/$MDEV
				return $ret
			elif $(grep -q ^$PWD/$md /proc/mounts); then
				(cd /dev && ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$md /usr/sbin/hot.sh)
				mdadm --stop $PWD/$md
				mdadm --incremental --run $PWD/$other
			else
				mdadm --stop $PWD/$md
				if test -n "$other"; then
					mdadm --incremental --run $PWD/$other
				fi
				return $ret
			fi
		fi
	fi

	if test "$ret" = "0"; then
		sed -i '\|^'$PWD/$MDEV'|d' /etc/fstab
	fi
	return $ret	

elif test "$ACTION" = "add" -a "$PHYSDEVDRIVER" = "usblp"; then
	sysd="/sys/class/usb/$MDEV//device/ieee1284_id"
	if test -f "$sysd"; then
	  eval $(sed -e 's/:/="/g' -e 's/;/";/g' "$sysd") >/dev/null 2>&1
	fi
	model=${MDL:-$MODEL}
	mfg=${MFG:-$MANUFACTURER}

	mkdir /var/spool/lpd/$MDEV
	if test -f /etc/printcap-safe; then
		echo "$MDEV|$mfg $model" >> /etc/printcap-safe
	else
		echo "$MDEV|$mfg $model" >> /etc/printcap
		rcsmb reload
	fi

elif test "$ACTION" = "remove" -a "$PHYSDEVDRIVER" = "usblp"; then
	rmdir /var/spool/lpd/$MDEV
	PCAP=/etc/printcap
	if test -e /etc/printcap-safe; then
		PCAP=/etc/printcap-safe
	fi
	sed -i '/^'$MDEV'/d' $PCAP

	if test -e $PCAP -a ! -s $PCAP; then
		rm $PCAP
	fi
	rcsmb reload

else
	logger "hot.sh: WHAT"
	logger "$(env)"
fi
