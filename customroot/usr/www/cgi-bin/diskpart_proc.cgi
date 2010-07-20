#!/bin/sh

. common.sh
check_cookie
read_args

#debug

if test -n "$Partition"; then
	dsk="$Partition"
	if ! eject $dsk > /dev/null; then
		# this makes sense, as some partitions can be preserved
		msg "Couldn't unmount disk $dsk for partitioning it"
	fi

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
				RAID) id=da ;;
				vfat) id=c ;;
				ntfs) id=7 ;;
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

	res=$(sfdisk -uS /dev/$dsk < $FMTFILE 2>&1)
	st=$?
	rm -f $FMTFILE
	if test $st != 0; then
		msg "Partitioning $dsk failed:\n\n$res"
	fi

	sleep 1

	while ! eject $dsk >& /dev/null; do
		usleep 300000
	done

	sfdisk -R /dev/$dsk >& /dev/null

	for pl in 1 2 3 4; do

		part=/dev/${dsk}${pl}
		ppart=$(basename $part)

		if test "$(eval echo \$keep_$ppart)" = "yes"; then continue; fi

		type=$(eval echo \$type_$ppart)
		rtype=$(eval echo \$raid_$ppart)
		pair1=$(eval echo \$pair1_$ppart)
		pair2=$(eval echo \$pair2_$ppart)

# this is dubious... in order to clean any traces of the previous filesystem
# on a given partition, that blkid will find regardeless of the partition ID,
# shall we clear the beginning os the partition with dd?

		case "$type" in				
			swap) 	mkswap $part
					continue ;;

			vfat)	dd if=/dev/zero of=$part bs=512 count=1 >& /dev/null
					continue ;;

			linux|ntfs|empty)
					continue ;;
		esac

		# raid case
		opts=""
		rspare=""

		case "$rtype" in
			none)	continue
					;;

			JBD)	if test "$pair1" = "missing"; then
						echo "To create a $rtype on $ppart you must specify a device to pair with"
					fi
					rlevel=linear
					ndevices=2
					;;

			raid0)	if test "$pair1" = "missing"; then
						echo "To create a $rtype on $ppart you must specify a device to pair with"
					fi
					rlevel=0
					ndevices=2
					;;

			raid1)	if test "$pair2" != "missing"; then
						rspare="--spare-devices=/dev/$pair2"
					fi
					opts="--bitmap=internal"
					rlevel=1
					ndevices=2
					;;

			raid5)	if test "$pair1" = "missing"; then
						echo "To create a $rtype on $ppart you must specify a device to pair with"
					fi
					if test "$pair2" != "missing"; then
						rspare="/dev/$pair2"
					else
						rspare="$pair2"
					fi
					opts="--bitmap=internal"
					rlevel=5
					ndevices=3
					;;

		esac

		if test "$pair1" != "missing"; then
			pair1="/dev/$pair1"
		fi

		for i in $(seq 0 9); do
			if ! test -b /dev/md$i; then
				MD=md$i
				break
			fi
		done

		res=$(mdadm --create /dev/$MD --run \
			--level=$rlevel --metadata=0.9 $opts \
			--raid-devices=$ndevices /dev/$ppart $pair1 $rspare 2>&1)

		if test "$?" != 0; then
			msg "Partitioning succeeded but creating RAID on $ppart failed:\n\n$res"
		fi

	done

else
	debug
fi

#enddebug
gotopage /cgi-bin/diskpart.cgi?disk=$dsk

