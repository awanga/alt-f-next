#!/bin/sh

debug=true

if test -n "$debug"; then
	exec >> /tmp/hot.log 2>&1
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

	res=$(mdadm --query --examine --export --test $PWD/$MDEV)
	if test $? = 0; then
		if ! test -f /etc/mdadm.conf; then
			mdadm --examine --scan > /etc/mdadm.conf
			echo "DEVICE /dev/sd*" >> /etc/mdadm.conf
		fi                                                            
		mdadm --incremental --run $PWD/$MDEV

		eval $res
		if test -z "$MD_NAME"; then # dlink formated MD doesnt have the MD_NAME attribute
			MD_NAME=$(ls /sys/block/${MDEV:0:3}/$MDEV/holders/)
			MD_NAME=${MD_NAME:2}
			dlink="yes"
		else
			MD_NAME=${MD_NAME##*:} # remove host: part
		fi
		if test -e $PWD/md$MD_NAME -a -b $PWD/md$MD_NAME; then
			mdadm --query --detail $PWD/md$MD_NAME
			# this is needed to generate a *new* md? event when the 2nd disk is inserted. It mounts the device as soon as possible. It has the inconvenient that when the 2nd disk is added it is rsynced. For linear and raid 0 this is fine, but not for raid1 or 5. FIXME
			if test $? = 0 -a -z "$dlink"; then # generate hotplug event for /dev/md?. 
#				echo "add" > /sys/block/md$MD_NAME/uevent
				(cd /dev && ACTION=add DEVTYPE=partition PWD=/dev MDEV=md$MD_NAME /usr/sbin/hot.sh)
			fi
		fi
		return 0
	fi

	fstype=$(blkid -s TYPE -o value -w /dev/null -c /dev/null $PWD/$MDEV)
	case $fstype in
		ext2|ext3|ext4|vfat|iso9660)
			;;
		ntfs) fstype="ntfs-3g"
			;; 
		swap)
			swapon -p 1 $PWD/$MDEV
			sed -i '\|^'$PWD/$MDEV'|d' /etc/fstab
			echo "$PWD/$MDEV none swap pri=1 0 0" >> /etc/fstab
			return 0
				;;
		*)
			logger "hot: unknown partition type $fstype"
			return 0
				;;
	esac

	lbl=$(blkid -s LABEL -o value -w /dev/null -c /dev/null $PWD/$MDEV | tr ' ' '_')
#	if test -z "$lbl" -o -d /mnt/$lbl; then lbl=$MDEV; fi # FIXME handle duplicate labels
	if test -z "$lbl"; then lbl=$MDEV; fi
	/bin/mkdir /mnt/$lbl
	if mountpoint /mnt/$lbl; then exit 0; fi
#	if test $? = 1; then exit 1; fi

	echo heartbeat > "/sys/class/leds/power:blue/trigger"
	res="$(fsck -p $PWD/$MDEV 2>&1)"
	if test $? -ge 2; then fsflg="-o ro"; fi
	logger "$res"
	echo default-on > "/sys/class/leds/power:blue/trigger"
	/bin/mount -t $fstype $fsflg $PWD/$MDEV /mnt/$lbl
	sed -i '\|^'$PWD/$MDEV'|d' /etc/fstab
	echo "$PWD/$MDEV /mnt/$lbl $fstype defaults 0 0" >> /etc/fstab
	if test -d "/mnt/$lbl/Users"; then
		if ! test -h /home -a -d "$(readlink -f /home)" ; then
			ln -s "/mnt/$lbl/Users" /home
		fi
	fi
	if test -d "/mnt/$lbl/ffp"; then
		if ! test -h /ffp -a -d "$(readlink -f /ffp)" ; then
			ln -s "/mnt/$lbl/ffp" /ffp
			if test $? = 0 -a -x /etc/init.d/S99ffp; then
					/etc/init.d/S99ffp start
			fi
		fi
	fi
	if test -d /mnt/$lbl/Alt-F; then
		if ! test -h /Alt-F -a -d "$(readlink -f /Alt-F)"; then
			rm /mnt/$lbl/Alt-F/Alt-F /mnt/$lbl/Alt-F/ffp
			ln -s /mnt/$lbl/Alt-F /Alt-F
			loadsave_settings -ta
			mount -t aufs -o remount,prepend:/mnt/$lbl/Alt-F=rw aufs /
		fi
	fi


elif test "$ACTION" = "add" -a "$DEVTYPE" = "disk"; then

	# md disk
	if test -d /sys/block/$MDEV/md; then
		echo $MDEV: NO PARTITION BASED MD, neither dlink created raid.

	# "normal" disk (not md)
	#elif test -d /sys/block/$MDEV/device; then 
	else

		# which bay?
		sed -i '\|'$MDEV'|d' /etc/bay
	
		# dont use PHYSDEVPATH, for easy mounting disks in /etc/init.d/rcS 
		PHYSD=$(readlink /sys/block/$MDEV/device) 
		if $(echo $PHYSD | grep -q /host0/); then
			bay="right"
		elif $(echo $PHYSD | grep -q /host1/); then
			bay="left"
		elif $(echo $PHYSD | grep -q /usb1/); then
			bay="usb"
		fi
	
		if test -n "$bay"; then
			echo "$bay $MDEV" >> /etc/bay
	
			# set disk spin down
			tm=$(awk '/'$bay'/{print $2}' /etc/hdsleep.conf )
		
			if test "$tm" -le "20"; then
				val=$((tm * 60 / 5))
			elif test "$tm" -le "300"; then
				val=$((240 + tm / 30))
			fi
	
			if test -n "$tm"; then
				hdparm -S $val $PWD/$MDEV
			fi
		fi
	
		# no low latency (server, not desktop)
		echo 0 > /sys/block/$MDEV/queue/iosched/low_latency
	
		# for now use only disk partition-based md
		fdisk -l $PWD/$MDEV | awk '/^\/dev\// && $5 == "fd" { exit 1 }'   
		if test $? = 1; then                                              
			if ! test -f /etc/mdadm.conf; then
				mdadm --examine --scan > /etc/mdadm.conf
				echo "DEVICE /dev/sd*" >> /etc/mdadm.conf
			fi                                                            
			# mdadm --assemble --auto=no --scan                                        
		fi
	fi

elif test "$ACTION" = "remove" -a "$DEVTYPE" = "disk"; then

	# remove some modules (repeat it while there are some?)
	lsmod | awk '{if ($3 == 0) system("modprobe -r " $1)}'

	PHYSD=$PHYSDEVPATH
	sed -i '\|'$MDEV'$|d' /etc/bay

	# which bay?
	# PHYSD=$(readlink /sys/block/$MDEV/device) 

elif test "$ACTION" = "remove" -a "$DEVTYPE" = "partition"; then

	ret=0

	#lbl=$(blkid -s LABEL -o value -w /dev/null -c /dev/null $PWD/$MDEV | tr ' ' '_')
	#if test -z "$lbl"; then lbl=$MDEV; fi
	mpt=$(awk '/'$MDEV'/{print $2}' /proc/mounts )
	if $(grep -q -e ^$PWD/$MDEV /proc/swaps); then
		swapoff $PWD/$MDEV
		ret=$?
	elif $(grep -q -e ^$PWD/$MDEV /proc/mounts); then
		if test "$(readlink -f /ffp)" = "$mpt/ffp"; then
			if test -x /etc/init.d/S99ffp; then
				/etc/init.d/S99ffp stop
			fi
			rm -f /ffp
		fi
 		if test "$(readlink -f /Alt-F)" = "$mpt/Alt-F"; then
 			mount -t aufs -o remount,del:$mpt/Alt-F aufs /
			if test $? = "0"; then
				loadsave_settings -fa
				rm -f /Alt-F
			else
				exit	# busy?
			fi
 		fi
		if test "$(readlink -f /home)" = "$mpt/Users"; then
			rm -f /home
		fi
		# umount $PWD/$MDEV
		umount $mpt
		ret=$?
		if test "$ret" = "0"; then
			rmdir $mpt
		fi
	elif test -e /proc/mdstat -a -n "$(grep $MDEV /proc/mdstat)"; then
		eval $(mdadm --examine --export $PWD/$MDEV)
		md=md${MD_NAME##*:} # remove host: part
		type=$MD_LEVEL
		if test -n "$md" -a -b $PWD/$md ; then
			act=$(cat /sys/block/$md/md/array_state)
			eval $(mdadm --detail $PWD/$md | awk \
				'/Active Devices/{ printf "actdev=%s;", $4}
				/Working Devices/{ printf "workdev=%s;", $4}')
			if test "$actdev" = 2; then # FIXME
				other=$(ls /sys/block/$md/slaves/ | grep -v $MDEV)
			fi
			if test "$act" != "inactive" -a "$type" = "raid1" -a "$actdev" = 2; then
				mdadm $PWD/$md --fail $PWD/$MDEV --remove $PWD/$MDEV
				return $ret
			elif $(grep -q ^$PWD/$md /proc/mounts); then
				#echo "remove" > /sys/block/$md/uevent
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
