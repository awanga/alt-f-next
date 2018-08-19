#!/bin/sh

. common.sh

check_cookie
read_args

#debug

CONFF=/etc/misc.conf

if test -f $CONFF; then
	. $CONFF
fi

# default Alt-F Volume Group name
VG=altf

run() {
	if ! res=$($* 2>&1); then msg "$res"; fi
}

# Volume Group options
if test -n "$VGCreate"; then
	if ! pvdisplay -s /dev/$pdev >& /dev/null; then
		run pvcreate /dev/$pdev
	fi

	run vgcreate $VG /dev/$pdev

elif test -n "$Destroy"; then
	vg=$Destroy
	rmdev=$(pvscan 2>/dev/null | while read pvl dsk lvg vgl rst; do
		if test "$vgl" = altf; then
			echo $dsk
		fi
	done)

	run vgremove -f $vg
	run pvremove -f $rmdev

elif test -n "$Add"; then
	i=$Add
	pdev=$(eval echo \$pdev_$i)
	if ! pvdisplay -s /dev/$pdev >/dev/null; then
		run pvcreate /dev/$pdev
	fi

	run vgextend $VG /dev/$pdev

elif test -n "$Remove"; then
	i=$Remove
	pdev=$(eval echo \$pdev_$i)

	run vgreduce $VG /dev/$pdev

# physical volumes
 
elif test -n "$Empty"; then
	i=$Empty
	pdev=$(eval echo \$pdev_$i)

	ndevs=$(pvs -o pv_name --noheadings | wc -l)
	inuse=$(pvdisplay --map /dev/$pdev 2> /dev/null | sed -n -e '/mlog/d' \
		-e 's/_mimage_.*//' -e '\|Logical volume|s|.*dev/||p')

	for i in $inuse; do
		type=$(lvs -o segtype --noheadings $i | tr -d ' ')
		if test "$type" = "mirror"; then
			# mirrors can't be pmoved, convert to linear first. User was warned!
			run lvm lvconvert -m0 $i /dev/$pdev
		elif test "$type" = "striped" -a "$ndevs" -lt 3; then
			msg "At least three Physical Volumes must exist to empty a stripped volume"
		elif test "$type" = "linear" -a "$ndevs" -lt 2; then
			msg "At least two Physical Volumes must exist to empty a linear volume"
		fi
	done

	run pvmove -b /dev/$pdev

elif test -n "$rmMissing"; then

	run vgreduce --removemissing altf #FIXME, VG

# Logical Volume options:
elif test "$action" = "Create"; then
	if test "$type" = "Linear"; then
		:
	elif test "$type" = "Mirror"; then
		flg="-m1"
	elif test "$type" = "Stripped"; then
		flg="-i2"
	fi

	run lvcreate --size ${lvsize}G $flg $VG 

elif test -n "$delete"; then
	i=$delete
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)

	# find /dev/dm-
	#eval $(dmsetup info /dev/$vg/$ldev | awk '/Major/{printf "mj=%d mi=%d", $3, $4}')
	#eval $(awk '/'$mj' *'$mi'/{printf "tdm=%s", $4}' /proc/partitions)
	tdm=$(find_dm $vg $ldev)

	if ismount $tdm; then umount /dev/$tdm; fi # FIXME fstab 

	run lvremove -f /dev/$vg/$ldev 

elif test -n "$tolinear"; then
	i=$tolinear
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)
	run lvm lvconvert -m0 /dev/$vg/$ldev 

elif test -n "$tomirror"; then
	i=$tomirror
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)
	run lvm lvconvert -b -m1 /dev/$vg/$ldev 

elif test -n "$csnap"; then
	i=$csnap
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)
	nsize=$(expr $(lvs --noheadings --nosuffix --units s -o lv_size $vg/$ldev) / 5)
	run lvcreate -s --size ${nsize}s -n ${ldev}_snap /dev/$vg/$ldev

elif test -n "$msnap"; then
	i=$msnap
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)
	odev=${ldev%_snap}

	tdm=$(find_dm $vg $odev)
	if ismount $tdm; then
		( cd /dev; ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$tdm /usr/sbin/hot.sh)
		if test $? != 0; then
			msg "Couldn't unmount /dev/$1/$2 for snapshot merging, stop services first."
		fi
	fi

	run	lvchange -a n /dev/$vg/$odev
	run lvm lvconvert --merge /dev/$vg/$ldev
	run lvchange -a y /dev/$vg/$odev

elif test -n "$split"; then
	i=$split
	vg=$(eval echo \$vg_$i)
    ldev=$(eval echo \$ldev_$i)
	run lvm lvconvert --splitmirrors 1 --name ${ldev}_split /dev/$vg/$ldev

elif test -n "$Enlarge"; then
	i=$Enlarge
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)
	cap=$(eval echo \$ncap_$i)
	run lvextend --size +${cap}G /dev/$vg/$ldev

elif test -n "$Shrink"; then
	i=$Shrink
	vg=$(eval echo \$vg_$i)
	ldev=$(eval echo \$ldev_$i)
	cap=$(eval echo \$ncap_$i)
	run lvreduce -f --size -${cap}G /dev/$vg/$ldev

fi

#enddebug
gotopage /cgi-bin/lvm.cgi
