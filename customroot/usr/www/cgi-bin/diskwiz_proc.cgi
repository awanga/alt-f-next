#!/bin/sh

. common.sh
read_args
check_cookie

#debug

# $1=error message
err() {
	cat<<-EOF
		failed </p>
		<pre>$1</pre>
		<p> <strong> Error </strong> </p>
		<input type="button" value="Back" onclick="window.location.assign(document.referrer)"></p>
		</body></html>
	EOF
	exit 1
}

lmsg() {
	echo "<script type=text/javascript>
		alert(\"$1\")
		window.location.assign(document.referrer)
		</script></body></html>"
	exit 1
}

# $1=-r to load disk
ejectall() {
	local i dsk
	for i in $disks; do
		dsk=$(basename $i)
		if ! eject $1 $dsk > /dev/null; then
			lmsg "Couldn't stop disk $dsk"
		fi
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
	for i in $(sfdisk -l | awk '$6 == da || $a == fd {print $1}'); do
		mdadm -zero-superblock $i >& /dev/null
	done
}

# partition all disks
# $1=std|raid, $2=equal, with equal sized partitions
partition() {
	local i 

	cleanraid

	maxsect=""
	if test "$1" = "raid"; then
		ptype="da"
	else
		ptype="83"
	fi

	if test "$2" = "equal"; then
		maxsect=$(minsize)
	fi

	for i in $disks; do
		echo "<p>Partitioning disk $(basename $i)..."

		eval $(sfdisk -l -uS $i | tr '*' ' ' | awk '
			/cylinders/ {printf "cylinders=%d; heads=%d; sectors=%d", $3, $5, $7}')

		sect_cyl=$(expr $heads \* $sectors) # number of sectors per cylinder

		pos=$sectors # keep first track empty.
		nsect=1048576 # 512MB for swap
		rem=$(expr \( $pos + $nsect \) % $sect_cyl) # number of sectors past end of cylinder
		nsect=$((nsect - rem)) # make partition ends on cylinder boundary

		pos2=$((pos+nsect))
		nsect2=""
		par3=""
		if test -n "$maxsect"; then
			nsect2=$((maxsect - pos2))
			rem2=$(expr \( $pos2 + $nsect2 \) % $sect_cyl)
			nsect2=$((nsect2 - rem2))
			pos3=$((pos2+nsect2))
			par3="$pos3,,L"
		fi

		FMTFILE=$(mktemp -t sfdisk-XXXXXX)
		cat<<-EOF > $FMTFILE
			$pos,$nsect,S
			$pos2,$nsect2,$ptype
			$par3
		EOF

		# unmount/stop raid
		ejectall

		res=$(sfdisk -uS $i < $FMTFILE 2>&1)
		if test $? != 0; then
			rm -f $FMTFILE
			err "$res"
		fi
		rm -f $FMTFILE

		# eject again, sfdisk -R needs it
		sleep 5
		ejectall

		# make kernel reread part table
		sfdisk -R $i
		sleep 5
		ejectall
		echo " done.</p>"
	done
}

create_swap() {
	local i
	for i in $disks; do
		echo "<p>Creating swap in disk $(basename $i)..."
		res="$(mkswap ${i}1 2>&1)"
		if test $? != 0; then
			err "$res"
		else
			echo " done.</p>"
		fi
	done
}

# $1=dev
create_fs() {
		echo "<p>Creating $wish_fs filesystem on disk $(basename $1)..."
		res="$(mke2fs -T $wish_fs ${1} 2>&1)"
		if test $? != 0; then
			err "$res"
		else
			echo " done.</p>"
		fi
}

# $1=linear|raid0|raid1|raid5
create_raid() {
	for j in $(seq 0 9); do
		if ! test -b /dev/md$j; then
			MD=md$j
			break
		fi
	done

	eval $(cat /etc/bay | sed -n 's/ /=/p')

	opts=""; pair1=/dev/${left}2; pair2=/dev/${right}2; spare=""
	case "$1" in
		linear)	;;
		raid0)	;;
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
	res="$(mdadm --create /dev/$MD --run \
		--level=$1 --metadata=0.9 $opts \
		--raid-devices=$ndisks $pair1 $pair2 $spare 2>&1)"
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

has_disks
nusb="$(cat /etc/bay | grep usb | wc -l)"

rcall stop >& /dev/null

case $wish_part in
	notouch) ;;
	standard) standard ;;
	jbd) jbd ;;
	raid0) raid0 ;;
	raid1) raid1 ;;
	raid5) raid5 ;;
esac

if test -f /etc/mdadm.conf; then rm -f /etc/mdadm.conf; fi
ejectall -r

#enddebug

if test -f /tmp/firstboot; then
	pg=newuser.cgi
else
	pg=diskmaint.cgi
fi

cat<<-EOF
	</pre><p> <strong> Success </strong> </p>
	<script type="text/javascript">
		url = document.referrer
		url = url.substr(0,url.lastIndexOf("/")) + "/$pg"
		setTimeout("window.location.assign(url)", 2000);
	</script></body></html>
EOF

