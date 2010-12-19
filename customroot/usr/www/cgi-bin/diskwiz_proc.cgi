#!/bin/sh

. common.sh
read_args
check_cookie

#debug

# $1=error message
err() {
	busy_cursor_end
	cat<<-EOF
		failed </p>
		<pre>$1</pre>
		<p><strong>Error</strong></p>
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

# lower common size of all disks (in sectors)
minsize() {
	local i
	msz=9999999999

	for i in $disks; do
		sz=$(sfdisk -s $i)
		if test "$sz" -lt "$msz"; then
			msz=$sz
		fi
	done

	echo $(expr $msz \* 2) 
}

# remove raid superblock to avoid auto rebuild on partially created arrays
# if by hazard the new partition table fits a previous one
cleanraid() {
	for i in $(sfdisk -l | awk '$6 == "da" || $6 == "fd" {printf "%s ", $1}'); do
		mdadm --zero-superblock $i >& /dev/null
	done
}

# 4k align: $1=pos, $2=nsect, $4=maxsect
align() {
	local nsect pos rem naxsec
	pos=$1
	nsect=$2
	maxsect=$3

	if test $(expr $pos + $nsect) -gt $maxsect; then
		nsect=$(expr $maxsect - $pos)
	fi

	rem=$(expr $nsect % 8)
	if test $rem -ne 0; then
		nsect=$(expr $nsect - $rem) # floor to previous 4k alignement
	fi
	echo $nsect
}

# partition all disks
# $1=std|raid, $2=equal, with equal sized partitions
partition() {
	local i 

	ptype="83"
	if test "$1" = "raid"; then
		ptype="da"
	fi

	commonsect=""
	if test "$2" = "equal"; then
		commonsect=$(minsize)
	fi

	for i in $disks; do
		echo "<p>Partitioning disk $(basename $i)..."

		# clean traces of previous filesystems...
		for j in ${i}?; do
			dd if=/dev/zero of=$j count=100 >& /dev/null
		done

		eval $(sfdisk -l -uS $i | tr '*' ' ' | awk '
			/cylinders/ {printf "cylinders=%d; heads=%d; sectors=%d", $3, $5, $7}')

		sect_cyl=$(expr $heads \* $sectors) # number of sectors per cylinder
		maxsect=$(expr $cylinders \* $sect_cyl)
		if test "$2" != "equal"; then
			commonsect=$maxsect
		fi

		pos=64 # 4k aligned
		nsect=1048576 # 512MB for swap
		nsect=$(align $pos $nsect $maxsect)

		pos2=$(expr $pos + $nsect)
		nsect2=$(expr $commonsect - $pos2)
		nsect2=$(align $pos2 $nsect2 $maxsect)

		par3=""
		if test "$maxsect" != "$commonsect"; then
			pos3=$(expr $pos2 + $nsect2)
			nsect3=$(expr $maxsect - $pos3)
			nsect3=$(align $pos3 $nsect3 $maxsect)
			if test "$nsect3" -gt 0; then
				par3="$pos3,$nsect3,83"
			fi
		fi

		FMTFILE=$(mktemp -t sfdisk-XXXXXX)
		cat<<-EOF > $FMTFILE
			$pos,$nsect,S
			$pos2,$nsect2,$ptype
			$par3
		EOF

		# do it!
		res=$(sfdisk --force -uS $i < $FMTFILE 2>&1)
		if test $? != 0; then
			rm -f $FMTFILE
			err "$res"
		fi
		rm -f $FMTFILE

		sfdisk -R /dev/$1 >& /dev/null
		sleep 3

		# somehow, in this scenario, mdev does not remove device, only creates them
		rm -f ${i}[0-9]
		mdev -s

		echo " done.</p>"
	done
	cleanraid
}

create_swap() {
	local i
	for i in $disks; do
		echo "<p>Creating and activating swap in disk $(basename $i)..."
		res="$(mkswap ${i}1 2>&1)"
		if test $? != 0; then
			err "$res"
		else
			res="$(swapon -p 1 ${i}1 2>&1)"
			if test $? != 0; then
				err "$res"
			else
				echo " done.</p>"
			fi
		fi
	done
}

# $1=dev
create_fs() {
		local dev sec sf
		dev=$(basename $1)
		if test "${dev%%[0-9]}" = "md"; then
			sf=/sys/block/${dev}/size
		else
			sf=/sys/block/${dev:0:3}/${dev}/size
		fi
		eval $(awk '{ printf "min=%d", ($1 * 512 / 1000000000 * 0.6 + 30) / 60}' $sf)
		echo "<p>Creating $wish_fs filesystem on $(basename $1). It will take roughly "
		wait_count_start "$min minute(s)"
		res="$(mke2fs -T $wish_fs ${1} 2>&1)"
		st=$?
		wait_count_stop
		if test $st != 0; then
			err "$res"
		else
			echo ". Done.</p>"
		fi
}

# $1=linear|raid0|raid1|raid5
create_raid() {
	curdev=$(mdadm --examine --scan | awk '{ print substr($2, match($2, "md"))}')
	for dev in $(seq 0 9); do
		if ! echo $curdev | grep -q md$dev; then MD=md$dev break; fi
	done

	. /etc/bay
	usb=$(sed -n '/^usb/s/\(.*_dev=\)\(.*\)/\2/p' /etc/bay) # assume only one usb disk!

	opts=""; pair1=/dev/${left_dev}2; pair2=/dev/${right_dev}2; spare=""
	case "$1" in
		linear|raid0)
				if test $ndisks = 3; then
					spare="/dev/${usb}2"
				fi
				;;
		raid1)  opts="--bitmap=internal"
				if test $ndisks = 1; then
					pair2="missing"
					ndisks=2
				elif test $ndisks = 3; then
					spare="/dev/${usb}2"
					opts="$opts --spare-devices=1"
					ndisks=2
				fi
				;;
		raid5)  opts="--bitmap=internal"
				if test $ndisks = 3; then
					spare="/dev/${usb}2"
				fi
				;;
	esac

	echo "<p>Creating $1..."
	res="$(mdadm --create --run --level=$1 --metadata=0.9 $opts --raid-devices=$ndisks \
		/dev/$MD $pair1 $pair2 $spare 2>&1)"
	if test $? != 0; then
		err "$res"
	else
		echo " done.</p>"
	fi
}

standard() {
	local i

	partition
	create_swap
	for i in $disks; do
		create_fs ${i}2
	done
}

jbd() {
	partition raid
	create_swap
	create_raid linear
	create_fs /dev/$MD
}

raid0() {
	partition raid equal
	create_swap
	create_raid raid0
	create_fs /dev/$MD
}

raid1() {
	partition raid equal
	create_swap
	create_raid raid1
	create_fs /dev/$MD
}

raid5() {
	partition raid equal
	create_swap
	create_raid raid5
	create_fs /dev/$MD
}

if test "$wish_fs" != "ext2" -a "$wish_fs" != "ext3" -a \
		"$wish_fs" != "ext4";then
	msg "Unknown filesystem type $wish_fs"
fi

if test "$wish_part" != "notouch" -a "$wish_part" != "standard" -a \
		"$wish_part" != "jbd" -a "$wish_part" != "raid0" -a \
		"$wish_part" != "raid1" -a "$wish_part" != "raid5"; then
	msg "Unknown disk layout type $wish_part"
fi

if test "$advise" != "Abracadabra"; then
	msg "Unknown operation"
fi

html_header
echo "<center><h2>Disk Wizard</h2></center>"
busy_cursor_start

has_disks

echo "<p>Stopping all services and disks..."
eject -a

# stop hotplug
echo > /proc/sys/kernel/hotplug

echo " done.</p>"

case $wish_part in
	notouch) ;;
	standard) standard ;;
	jbd) jbd ;;
	raid0) raid0 ;;
	raid1) raid1 ;;
	raid5) raid5 ;;
esac

loadall

# restart hotplug
echo /sbin/mdev > /proc/sys/kernel/hotplug

#enddebug

if test -f /tmp/firstboot; then
	pg=newuser.cgi
else
	pg=diskmaint.cgi
fi

busy_cursor_end

cat<<-EOF
	</pre><p><strong>Success!</strong></p>
	<script type="text/javascript">
		url = document.referrer
		url = url.substr(0,url.lastIndexOf("/")) + "/$pg"
		setTimeout("window.location.assign(url)", 3000);
	</script></body></html>
EOF
