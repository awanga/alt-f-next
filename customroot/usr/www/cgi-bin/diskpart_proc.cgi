#!/bin/sh

. common.sh
check_cookie
read_args

CONFT=/etc/fstab

#debug

# FIXME: deal with errors
pre() {
	html_header
	echo "<center><h2>Disk Partitioner</h2></center>"
	busy_cursor_start

	echo "<p>Stopping all services...</p>"
	rcall stop >& /dev/null
	echo "<p>Stopping all disks...</p>"
	ejectall
}

# $1=-r to load
ejectall() {
	for i in $(ls /dev/sd? 2>/dev/null); do
		if ! eject $1 $(basename $i) > /dev/null; then
			echo "<p>Couldn't stop disk $(basename $i)</p>"
			fail=true
			return 1
		fi
	done
}

fail=""
if test -n "$cp_from"; then
	eval cp_to=$(echo \$cp_$cp_from)

	pre
	echo "<p>Copying partition table from $cp_from to ${cp_to}...</p>"

	TFILE=$(mktemp -t sfdisk-XXXXXX)
	sfdisk -d /dev/$cp_from > $TFILE
	res="$(sfdisk --force /dev/$cp_to < $TFILE 2>&1)"
	st=$?
	rm -f $TFILE
	if test $st != 0; then
		echo "<p>Copying failed:</p><pre>$res</pre>"
		fail=true
	fi
	sfdisk -R /dev/$cp_to >& /dev/null
	sleep 5
	blkid -c /dev/null >& /dev/null
	dsk=$cp_to

elif test -n "$Erase"; then
	dsk=${Erase#op_}
	
	pre
	echo "<p>Erasing partition table from ${dsk}...</p>"

	# erase also the MBR id (sector last 2 bytes, otherwise would be count=64)
	dd if=/dev/zero of=/dev/$dsk bs=1 count=66 seek=446 >& /dev/null
	sfdisk -R /dev/$dsk >& /dev/null
	sleep 5
	blkid -c /dev/null >& /dev/null

elif test -n "$Save"; then
	dsk=${Save#op_}
	#echo Save=$dsk
	sfdisk -d /dev/$dsk > /tmp/saved_${dsk}_part 2> /dev/null
	gotopage /cgi-bin/diskpart.cgi?disk=$dsk

elif test -n "$Load"; then
	dsk=${Load#op_}

	if ! test -f /tmp/saved_${dsk}_part; then
		msg "File /tmp/saved_${dsk}_part does not exists.\n\n\
In order to Load, you have to first save the disk partition."
	fi

	if grep -q "No partitions found" /tmp/saved_${dsk}_part; then
		msg "The loaded file doesn't contain a valid partition table."
	fi

	pre
	echo "<p>Loading partition table to ${dsk}...</p>"

	res="$(sfdisk /dev/$dsk < /tmp/saved_${dsk}_part 2>&1)"
	if test $? != 0; then
		echo "<p>Loading partition table failed:</p><pre>$res</pre>"
		fail=true
	fi

	sfdisk -R /dev/$dsk >& /dev/null
	sleep 5
	blkid -c /dev/null >& /dev/null
	
elif test -n "$Partition"; then
	dsk="$Partition"

	FMTFILE=$(mktemp -t sfdisk-XXXXXX)

	fout=$(sfdisk -l -uS /dev/$dsk | tr '*' ' ') # *: the boot flag...

	eval $(echo "$fout" | awk '
		/cylinders/ {printf "cylinders=%d; heads=%d; sectors=%d", $3, $5, $7}')

	#pos=$sectors # keep first track empty.
	pos=64 # 4k aligned, assuming offset=1. sfdisk will complain, use -f
	sect_cyl=$(expr $heads \* $sectors) # number of sectors per cylinder
	maxsect=$(expr $cylinders \* $sect_cyl)

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
				RAID) id=da  ;;
			esac

			if test $(expr $pos % 8) -ne 0; then
				pos=$(expr $pos + 8 - $pos % 8)	# ceil to next 4k alignement
			fi

			nsect=$(eval echo \$cap_$ppart | awk '{printf "%d", $0 * 1e9/512}')

			if test "$id" = 0 -a "$nsect" = 0; then
				echo "0,0,0" >> $FMTFILE
			else
# dont honour cylinder boundary alignement, its obsolete and unnecessary
#				rem=$(expr \( $pos + $nsect \) % $sect_cyl) # number of sectors past end of cylinder
#				nsect=$(expr $nsect - $rem) # make partition ends on cylinder boundary
				if test $(expr $pos + $nsect) -gt $maxsect; then
					nsect=$(expr $maxsect - $pos)
				fi
				rem=$(expr $nsect % 8)
				if test $rem -ne 0; then
					nsect=$(expr $nsect - $rem) # floor to previous 4k alignement
				fi
				echo "$pos,$nsect,$id" >> $FMTFILE
				pos=$((pos + nsect))
			fi
		fi
		last=$ppart
	done

	pre

	echo "<p>Partitioning disk $dsk...</p>"

	res=$(sfdisk --force -uS /dev/$dsk < $FMTFILE 2>&1) # sfdisk don't like 4k aligned partitions
	st=$?
	rm -f $FMTFILE
	if test $st != 0; then
		echo "<p>Partitioning $dsk failed:<p><pre>$res</pre>"
		fail=true
	fi

	# eject again, sfdisk -R needs it
	echo "<p>Stopping all disks again...</p>"
	sleep 5
	ejectall

	# make kernel reread part table
	echo "<p>Make kernel re-read partition table...</p>"
	sfdisk -R /dev/$dsk >& /dev/null

	# eject again, as hotplugging is enabled and we want no raid/swap/mount  
	echo "<p>Stopping all disks again...</p>"
	sleep 5
	ejectall

	allst=0
	allres="Partitioning succeeded but some RAID operations failed:"

	# now setup some filesystem and raid on created partitions
	echo "<p>Setting up partitions details... </p>"
	for pl in 1 2 3 4; do

		part=/dev/${dsk}${pl}
		ppart=$(basename $part)

		if test "$(eval echo \$keep_$ppart)" = "yes"; then continue; fi

		type=$(eval echo \$type_$ppart)

# in order to clean any traces of the previous filesystem on a given partition,
# that blkid will find regardeless of the partition ID,
# shall we clear the beginning/end of the partition with dd?

		case "$type" in				
			swap)
				mkswap $part >& /dev/null
				;;

			vfat)
				# clean raid superblock, otherwise blkid will report it as mdraid
				mdadm  --zero-superblock $part >& /dev/null
				# s/fdisk say to do it
				dd if=/dev/zero of=$part bs=512 count=1 >& /dev/null
				;;

			raid|linux|ntfs|empty)
				# clean raid superblock, otherwise blkid will report it as mdraid
				mdadm  --zero-superblock $part >& /dev/null
				;;
		esac
	done

	# reload disks
	echo "<p>Reloading all disks...</p>"
	blkid -c /dev/null >& /dev/null
	ejectall -r
fi
	
busy_cursor_end

if test -z "$fail"; then
	cat<<-EOF
		<p><strong>Success</strong></p>
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
			setTimeout("err()", 2000);
		</script>
		</body></html>
EOF
#	js_gotopage /cgi-bin/diskpart.cgi?disk=$dsk
else
	back_button
fi

#enddebug
