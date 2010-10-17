#!/bin/sh

. common.sh
check_cookie
read_args

CONFT=/etc/fstab

#debug

# $1=-r to load
ejectall() {
	for i in $(ls /dev/sd? 2>/dev/null); do
		if ! eject $1 $(basename $i) > /dev/null; then
			msg "Couldn't stop disk $(basename $i)"
		fi
	done
}

if test -n "$cp_from"; then
	eval cp_to=$(echo \$cp_$cp_from)
	#echo copy from $cp_from to $cp_to

	rcall stop >& /dev/null
	ejectall

	TFILE=$(mktemp -t sfdisk-XXXXXX)
	sfdisk -d /dev/$cp_from > $TFILE
	sfdisk /dev/$cp_to < $TFILE >& /dev/null
	rm -f $TFILE
	sfdisk -R /dev/$cp_to >& /dev/null
	sleep 5
	blkid -c /dev/null >& /dev/null

elif test -n "$Erase"; then
	dsk=${Erase#op_}
	#echo erase=$dsk

	rcall stop >& /dev/null
	ejectall

	dd if=/dev/zero of=/dev/$dsk bs=1 count=64 seek=446 >& /dev/null
	sfdisk -R /dev/$dsk >& /dev/null
	sleep 5
	blkid -c /dev/null >& /dev/null

elif test -n "$Save"; then
	dsk=${Save#op_}
	#echo Save=$dsk
	sfdisk -d /dev/$dsk > /tmp/saved_${dsk}_part 2> /dev/null

elif test -n "$Load"; then
	dsk=${Load#op_}
	#echo load=$dsk

	if ! test -f /tmp/saved_${dsk}_part; then
		msg "File /tmp/saved_${dsk}_part does not exists.\n\n\
In order to Load, you have to first save the disk partition."
	fi

	rcall stop >& /dev/null
	ejectall

	res="$(sfdisk /dev/$dsk < /tmp/saved_${dsk}_part 2>&1)"
	if test $? != 0; then
		msg "$res"
	fi
	sfdisk -R /dev/$dsk >& /dev/null
	sleep 5
	blkid -c /dev/null >& /dev/null
	
elif test -n "$Partition"; then

	dsk="$Partition"

# play safe, "stop" all disks. This mean unmounting, unswapping, stopping raid
# if there are active raid devices, they are probably using 
# some of this disk partitions

	rcall stop >& /dev/null
	ejectall

	FMTFILE=$(mktemp -t sfdisk-XXXXXX)

	fout=$(sfdisk -l -uS /dev/$dsk | tr '*' ' ') # *: the boot flag...

	eval $(echo "$fout" | awk '
		/cylinders/ {printf "cylinders=%d; heads=%d; sectors=%d", $3, $5, $7}')

	pos=$sectors # keep first track empty.
	sect_cyl=$(expr $heads \* $sectors) # number of sectors per cylinder

	if $(echo $fout | grep -q "No partitions found"); then
		fout="/dev/${dsk}1          0       -       0          0    0  Empty
/dev/${dsk}2          0       -       0          0    0  Empty
/dev/${dsk}3          0       -       0          0    0  Empty
/dev/${dsk}4          0       -       0          0    0  Empty"
	fi

	for pl in 1 2 3 4; do

		part=/dev/${dsk}${pl}
		ppart=$(basename $part)
		id=""; type="";cap=""
		eval $(echo "$fout" | awk '
			/'$ppart'/{printf "start=%d; end=%d; sects=%d; id=%s", \
			$2,  $3, $4, $5}')

		if test "$(eval echo \$keep_$ppart)" = "yes"; then
			if test "$pos" -gt "$start" -a "$id" != 0 -a "$sects" != 0; then
				rm -f $FMTFILE
				msg "Partition $last is too big, it extends over $ppart,\nor\npartitions are not in order"
			fi
			if test "$id" = 0 -a "$sects" = 0; then
				echo "0,0,0" >> $FMTFILE
			else
				echo "$start,$sects,$id" >> $FMTFILE
				pos=$((start + sects))
			fi
		else
			case "$(eval echo \$type_$ppart)" in
				empty) id=0 ;;
				swap) id=82 ;;
				linux) id=83 ;;
				vfat) id=c ;;
				ntfs) id=7 ;;
				RAID) id=da 
					rtype=$(eval echo \$raid_$ppart)
					pair1=$(eval echo \$pair1_$ppart)

					# verify raid setting 
					case "$rtype" in
						none|raid1)
							;;

						JBD|raid0|raid5)
							if test "$pair1" = "none"; then
								msg "To create a $rtype on $ppart you must specify a device to pair with"
							fi
							;;
					esac
					;;
			esac

			nsect=$(eval echo \$cap_$ppart | awk '{printf "%d", $0 * 1e9/512}')
			if test "$id" = 0 -a "$nsect" = 0; then
				echo "0,0,0" >> $FMTFILE
			else
				rem=$(expr \( $pos + $nsect \) % $sect_cyl) # number of sectors past end of cylinder
				nsect=$((nsect - rem)) # make partition ends on cylinder boundary
				echo "$pos,$nsect,$id" >> $FMTFILE
				pos=$((pos + nsect))
			fi
		fi
		last=$ppart
	done

	# partitioning can make devices appear/disappear, so stop hot-plugging
	# disabling hotplug seems to avoid the kernel to reread the part table...
	# hot=$(cat /proc/sys/kernel/hotplug)
	# echo > /proc/sys/kernel/hotplug

	res=$(sfdisk -uS /dev/$dsk < $FMTFILE 2>&1)
	st=$?
	rm -f $FMTFILE
	if test $st != 0; then
		msg "Partitioning $dsk failed:\n\n$res"
	fi

	# eject again, sfdisk -R needs it
	sleep 5
	ejectall

	# make kernel reread part table
	sfdisk -R /dev/$dsk >& /dev/null

	# eject again, as hotplugging is enabled and we want no raid/swap/mount  
	sleep 5
	ejectall

	allst=0
	allres="Partitioning succeeded but some RAID operations failed:"

	# now setup some filesystem and raid on created partitions
	for pl in 1 2 3 4; do

		part=/dev/${dsk}${pl}
		ppart=$(basename $part)

		if test "$(eval echo \$keep_$ppart)" = "yes"; then continue; fi

		type=$(eval echo \$type_$ppart)
		rtype=$(eval echo \$raid_$ppart)
		pair1=$(eval echo \$pair1_$ppart)
		pair2=$(eval echo \$pair2_$ppart)

# in order to clean any traces of the previous filesystem on a given partition,
# that blkid will find regardeless of the partition ID,
# shall we clear the beginning/end of the partition with dd?

		case "$type" in				
			swap)
				mkswap $part >& /dev/null
				continue ;;

			vfat)
				# clean raid superblock, otherwise blkid will report it as mdraid
				mdadm  --zero-superblock $part >& /dev/null
				# s/fdisk say to do it
				dd if=/dev/zero of=$part bs=512 count=1 >& /dev/null
				continue ;;

			linux|ntfs|empty)
				# clean raid superblock, otherwise blkid will report it as mdraid
				mdadm  --zero-superblock $part >& /dev/null
				continue ;;
		esac

		# raid case
		opts=""
		rspare=""

		# settings verified above, just do it
		case "$rtype" in
			none)	continue
				;;

			JBD)	pair1="/dev/$pair1"
				rlevel=linear
				ndevices=2
				;;

			raid0)	pair1="/dev/$pair1"
				rlevel=0
				ndevices=2
				;;

			raid1)
				opts="--bitmap=internal"	
				if test "$pair1" = "none"; then
					pair1="missing"
				else
					pair1="/dev/$pair1"
				fi
				if test "$pair2" != "none"; then
					opts="$opts --spare-devices=1"
					rspare="/dev/$pair2"
				fi
				
				rlevel=1
				ndevices=2
				;;

			raid5)	pair1="/dev/$pair1"
				if test "$pair2" = "none"; then
					rspare="missing"
				else
					rspare="/dev/$pair2"
				fi
				opts="--bitmap=internal"
				rlevel=5
				ndevices=3
				;;

		esac

		for i in $(seq 0 9); do
			if ! test -b /dev/md$i; then
				MD=md$i
				break
			fi
		done
		
		for i in $pair1 $rspare; do
			if grep -q $i /proc/mounts; then
				umount $i
				sed -i '\|^'$i'|d' $CONFT
			fi
		done

		res=$(mdadm --create /dev/$MD --run \
			--level=$rlevel --metadata=0.9 $opts \
			--raid-devices=$ndevices /dev/$ppart $pair1 $rspare 2>&1)
		st=$?
		# dont stop on one error, other operations can be successefull
		if test "$st" != 0; then
			allst=$((allst + $st))
			allres="$allres\n\nCreating RAID on $ppart failed:\n\n$res"
		fi
	done

	# reload disks
	if test -f /etc/mdadm.conf; then rm -f /etc/mdadm.conf; fi
	blkid -c /dev/null >& /dev/null
	ejectall -r

	# restart hot-plugging
	# echo "$hot" > /proc/sys/kernel/hotplug

	if test "$allst" != 0; then
		txt=$(echo "$allres" | awk '{printf "%s\\n", $0}')
		html_header
		cat<<-EOF
			<script type=text/javascript>
			alert("$txt")
			window.history.back()
			//window.location.assign(document.referrer)
			</script></body></html>
		EOF
	fi
else
	debug
fi

#enddebug
gotopage /cgi-bin/diskpart.cgi?disk=$dsk

