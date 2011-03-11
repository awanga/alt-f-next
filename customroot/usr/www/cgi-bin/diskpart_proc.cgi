#!/bin/sh

. common.sh
check_cookie
read_args

#debug

# FIXME: deal with errors
pre() {
	html_header
	echo "<center><h2>Disk Partitioner</h2></center>"
	busy_cursor_start

	echo "<p>Stopping disk..."
	if ! eject $dsk >& /dev/null ; then
		echo " failed</p>.<p>Trying to stop all services and disks...""
		if ! eject -a; then
			err ""
		fi
	fi

	# stop hotplug
	echo > /proc/sys/kernel/hotplug

	echo " done.</p>"
}

# $1=error message
err() {
	busy_cursor_end
	cat<<-EOF
		failed </p>
		<pre>$1</pre>
		<p><strong>Error</strong>
		<input type="button" value="Back" onclick="window.location.assign(document.referrer)"></p>
		</body></html>
	EOF
	# restart hotplug
	echo /sbin/mdev > /proc/sys/kernel/hotplug
	exit 1
}

# load all disk
loadall() {
	for i in $disks; do
		dsk=$(basename $i)
		eject -r $dsk >& /dev/null
	done
}

# $1=dsk
reread_part() {
	sfdisk -R /dev/$1 >& /dev/null
	sleep 3

	# somehow, in this scenario, mdev does not remove device, only creates them
	rm -f /dev/${1}[0-9]
	mdev -s
}

has_disks

if test -n "$cp_from"; then
	eval cp_to=$(echo \$cp_$cp_from)
	dsk=$cp_to

	pre
	echo "<p>Copying partition table from $cp_from to ${cp_to}..."

	TFILE=$(mktemp -t sfdisk-XXXXXX)
	sfdisk -d /dev/$cp_from > $TFILE
	res="$(sfdisk --force /dev/$cp_to < $TFILE 2>&1)"
	st=$?
	rm -f $TFILE
	if test $st != 0; then
		err "$res"
	fi

	reread_part $dsk

elif test -n "$Erase"; then
	dsk=${Erase#op_}
	
	pre
	echo "<p>Erasing partition table from ${dsk}..."

	# erase also the MBR id (sector last 2 bytes, otherwise would be count=64)
	dd if=/dev/zero of=/dev/$dsk bs=1 count=66 seek=446 >& /dev/null

	reread_part $dsk

elif test -n "$Save"; then
	dsk=${Save#op_}

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
	echo "<p>Loading partition table to ${dsk}..."

	res="$(sfdisk -f /dev/$dsk < /tmp/saved_${dsk}_part 2>&1)"
	if test $? != 0; then
		err "$res"
	fi

	reread_part $dsk
	
elif test -n "$Partition"; then
	dsk="$Partition"

	FMTFILE=$(mktemp -t sfdisk-XXXXXX)

	fout=$(sfdisk -l -uS /dev/$dsk | tr '*' ' ') # *: the boot flag...

	eval $(echo "$fout" | awk '
		/cylinders/ {printf "cylinders=%d; heads=%d; sectors=%d", $3, $5, $7}')

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

			rem=$(expr $pos % 8)
			if test $rem -ne 0; then
				pos=$(expr $pos + 8 - $rem)	# ceil to next 4k alignement
			fi

			nsect=$(eval echo \$cap_$ppart | awk '{printf "%d", $0 * 1e9/512}')

			if test "$id" = 0 -a "$nsect" = 0; then
				echo "0,0,0" >> $FMTFILE
			else
				if test $(expr $pos + $nsect) -gt $maxsect; then
					nsect=$(expr $maxsect - $pos)
				fi
				rem=$(expr $nsect % 8)
				if test $rem -ne 0; then
					nsect=$(expr $nsect - $rem) # floor to previous 4k alignement
				fi
				echo "$pos,$nsect,$id" >> $FMTFILE
				pos=$(expr $pos + $nsect)
			fi
		fi
		last=$ppart
	done

	pre
	echo "<p>Partitioning disk $dsk..."

	res=$(sfdisk --force -uS /dev/$dsk < $FMTFILE 2>&1) # sfdisk don't like 4k aligned partitions
	st=$?
	rm -f $FMTFILE
	if test $st != 0; then
		err "$res"
	fi

	reread_part $dsk

	allst=0
	allres="Partitioning succeeded but some RAID operations failed:"

	# now setup some filesystem and raid on created partitions
	echo " done</p><p>Setting up partitions details..."
	for pl in 1 2 3 4; do

		part=/dev/${dsk}${pl}
		ppart=$(basename $part)

		if test "$(eval echo \$keep_$ppart)" = "yes"; then continue; fi

		type=$(eval echo \$type_$ppart)

		# clean traces of previous filesystems...
		# NO, user might want to enlarge/shrink the filesystem
		# dd if=/dev/zero of=$part count=100 >& /dev/null

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
fi

# reload disks
echo " done</p><p>Reloading all disks..."
blkid -c /dev/null >& /dev/null

loadall

echo " done</p>"

# restart hotplug
echo /sbin/mdev > /proc/sys/kernel/hotplug

busy_cursor_end

cat<<-EOF
	<p><strong>Success</strong></p>
	<script type="text/javascript">
		function err() {
			window.location.assign(document.referrer)
		}
		setTimeout("err()", 3000);
	</script>
	</body></html>
EOF

#enddebug
