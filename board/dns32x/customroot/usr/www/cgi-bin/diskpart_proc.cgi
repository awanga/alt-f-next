#!/bin/sh

. common.sh
check_cookie
read_args

#debug

# FIXME: deal with errors
pre() {
	html_header "Disk Partitioner"
	busy_cursor_start

	echo "<p>Stopping disk $dsk..."
	if ! eject $dsk >& /dev/null ; then
		echo " failed.</p><p>Trying to stop all services and disks..."
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
reread_part() { # FIXME needed with GPT?
	sfdisk -R /dev/$1 >& /dev/null 
	sleep 3

	# somehow, in this scenario, mdev does not remove device, only creates them
	rm -f /dev/${1}[0-9]
	mdev -s
}

#$1-dsk
make_swap() {
	sout=$(sfdisk -l /dev/$1)
	pt=$(echo "$sout" | awk '/\/dev\//{if ($6 == "82") print $1}')
	if test -n "$pt"; then
		echo " done</p><p>Creating swap on $(basename $pt)..."
		mkswap $pt >& /dev/null
		return 0
	fi

	if test -n "$(echo "$sout" | awk '/\/dev\//{if ($6 == "ee") print $1}')"; then
	    gpt=$(sgdisk -p /dev/$1 | awk '{if ($6 == "8200") print $1}')
		if test -n "$gpt"; then
			echo " done</p><p>Creating swap on ${1}$gpt..."
			mkswap /dev/${1}$gpt >& /dev/null
		fi
	fi
}

# $1-dsk
finalize() {

	allst=0
	allres="Partitioning succeeded but some RAID operations failed:"

	# now setup some filesystem and raid on created partitions
	echo " done</p><p>Setting up partitions details..."
	for pl in 1 2 3 4; do

		part=/dev/${1}${pl}
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

			LVM|RAID|linux|"Windows Data"|ntfs|empty)
				# clean raid superblock, otherwise blkid will report it as mdraid
				mdadm  --zero-superblock $part >& /dev/null
				;;
		esac
	done
}

has_disks

if test -n "$cp_from"; then
	eval cp_to=$(echo \$cp_$cp_from)
	dsk=$cp_to

	pre
	echo "<p>Copying partition table from $cp_from to $cp_to..."

	if test "$in_use" = "MBR"; then
		sgdisk --zap-all /dev/$cp_to >& /dev/null
		res="$(sfdisk -d /dev/$cp_from | sfdisk --force /dev/$cp_to  2>&1)"
		if test $? != 0; then
			err "$res"
		fi
	elif test "$in_use" = "GPT"; then
		res=$(sgdisk --replicate=/dev/$cp_to /dev/$cp_from 2>&1)
		if test $? != 0; then
			err "$res"
		fi
		sgdisk --randomize-guids /dev/$cp_to >& /dev/null
	fi

	reread_part $dsk
	make_swap $dsk

elif test -n "$Erase"; then
	dsk=${Erase#op_}
	
	pre
	echo "<p>Erasing partition table from ${dsk}..."

	if test "$in_use" = "MBR"; then
		# erase also the MBR id (sector last 2 bytes, otherwise would be count=64)
		dd if=/dev/zero of=/dev/$dsk bs=1 count=66 seek=446 >& /dev/null
		sgdisk --zap /dev/$dsk >& /dev/null
	elif test "$in_use" = "GPT"; then
		sgdisk --zap-all /dev/$dsk >& /dev/null
	fi

	reread_part $dsk

elif test -n "$Save"; then
	dsk=${Save#op_}

	if test "$in_use" = "MBR"; then
		sfdisk -d /dev/$dsk > /tmp/saved_mbr_${dsk}_part 2> /dev/null
	elif test "$in_use" = "GPT"; then
		sgdisk --backup=/tmp/saved_gpt_${dsk}_part /dev/$dsk >& /dev/null
	fi
	gotopage /cgi-bin/diskpart.cgi?disk=$dsk

elif test -n "$Load"; then
	dsk=${Load#op_}

	fname=""
	if test "$in_use" = "MBR"; then
		fname=/tmp/saved_mbr_${dsk}_part
	elif test "$in_use" = "GPT"; then
		fname=/tmp/saved_gpt_${dsk}_part
	fi

	if ! test -f "$fname"; then
		msg "File $fname does not exists.\n\n\
In order to Load, you have to first save the disk partition."
	fi

	if test "$in_use" = "MBR"; then
		if grep -q "No partitions found" $fname; then
			msg "The loaded file doesn't contain a valid MBR partition table."
		fi
	fi

	pre
	echo "<p>Loading partition table to ${dsk}..."

	if test "$in_use" = "MBR"; then
		res="$(sfdisk --force /dev/$dsk < $fname 2>&1)"
	elif test "$in_use" = "GPT"; then
		res="$(sgdisk --load-backup=$fname /dev/$dsk 2>&1)"
	fi
	if test $? != 0; then
		err "$res"
	fi

	reread_part $dsk
	make_swap $dsk

elif test -n "$Conv_MBR"; then # GPT to MBR
	dsk=${Conv_MBR#op_}

	pre
	echo "<p>Converting ${dsk} disk GPT partition table to MBR..."

	pn=$(sgdisk -p /dev/$dsk | awk '/^Number/ {while (getline) pn=pn ":" $1; print pn}' 2> /dev/null)
	if test -z "$pn"; then
		res=$(sgdisk --zap-all /dev/$dsk >& /dev/null)
	else
		res=$(sgdisk --gpttombr $pn /dev/$dsk 2>&1)
	fi
	if test $? != 0; then
		msg "$res"
	fi

	reread_part $dsk

elif test -n "$Conv_GPT"; then # MBR to GPT
	dsk=${Conv_GPT#op_}

	pre
	echo "<p>Converting ${dsk} disk MBR partition table to GPT..."
	sgdisk --zap /dev/$dsk >& /dev/null
	res=$(sgdisk --mbrtogpt /dev/$dsk 2>&1)
	if test $? != 0; then
		msg "Conv_GPT $dsk: $res"
	fi

	reread_part $dsk
	
elif test -n "$Partition" -a "$in_use" = "MBR"; then
	dsk="$Partition"
	FMTFILE=$(mktemp -t sfdisk-XXXXXX)

	fout=$(sfdisk -l -uS /dev/$dsk | tr '*' ' ') # *: the boot flag...

	if $(echo $fout | grep -q "No partitions found"); then
		fout="/dev/${dsk}1          0       -       0          0    0  Empty
/dev/${dsk}2          0       -       0          0    0  Empty
/dev/${dsk}3          0       -       0          0    0  Empty
/dev/${dsk}4          0       -       0          0    0  Empty"
	fi

	for pl in 1 2 3 4; do
		part=/dev/${dsk}${pl}
		ppart=${dsk}${pl}

		if test "$(eval echo \$keep_$ppart)" = "yes"; then
			eval $(echo "$fout" | awk '
				/'$ppart'/{printf "start=%.0f; sects=%.0f; id=%s", $2, $4, $5}')
		else
			case "$(eval echo \$type_$ppart)" in
				empty) id=0 ;;
				swap) id=82 ;;
				linux) id=83 ;;
				LVM) id=8e ;;
				vfat) id=c ;;
				ntfs) id=7 ;;
				RAID) id=da  ;;
			esac

			start=$(eval echo \$start_$ppart)
			sects=$(eval echo \$len_$ppart)
		fi

		if test -z "$start" -o -z "$sects" -o "$sects" = 0; then
			echo "0,0,0" >> $FMTFILE
		else
			echo "$start,$sects,$id" >> $FMTFILE
		fi
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

	finalize $dsk

elif test -n "$Partition" -a "$in_use" = "GPT"; then
	dsk="$Partition"

	fout=$(sgdisk -p /dev/$dsk 2> /dev/null)
	parts=$(echo "$fout" | awk '/Number/ { while (getline) printf " %d", $1}')

	for pl in 1 2 3 4; do
		ppart=${dsk}${pl}
		if test "$(eval echo \$keep_$ppart)" = "yes"; then continue; fi
		if echo $parts | grep -q $pl; then dcmd="$dcmd --delete=$pl"; fi
	done

	for pl in 1 2 3 4; do
		part=/dev/${dsk}${pl}
		ppart=${dsk}${pl}
		id=""; type=""

		if test "$(eval echo \$keep_$ppart)" = "yes"; then continue; fi

		type=$(httpd -d $(eval echo \$type_$ppart))
		case "$type" in
			empty) id=0 ;;
			swap) id=8200 ;;
			linux) id=8300 ;;
			LVM) id=8e00 ;;
			RAID) id=fd00 ;;
			"Windows Data") id=0700 ;;
		esac

		spos=$(eval echo \$start_$ppart)
		slen=$(eval echo \$len_$ppart)
		if ! test -z "$spos" -o "$spos" = 0 -o -z "$slen" -o "$slen" = 0; then
			cmd="$cmd --new=$pl:$spos:$(expr $spos + $slen - 1) --typecode=$pl:$id"
		fi
	done

	pre
	echo "<p>Partitioning disk $dsk..."

	res=$(sgdisk --set-alignment=8 $dcmd $cmd /dev/$dsk 2>&1)
	if test $? != 0; then
		err "$res"
	fi

	reread_part $dsk

	finalize $dsk
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
