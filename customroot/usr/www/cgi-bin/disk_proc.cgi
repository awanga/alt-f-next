#!/bin/sh

unmount_part() {
    local lpart ret
    lpart=$1
    if $(grep -q /dev/$lpart /proc/mounts); then
	umount /dev/$lpart
	ret=$?
    elif $(grep -q /dev/$lpart /proc/swaps); then
	swapoff /dev/$lpart
	ret=$?
    fi
    return $ret
}

unmount_disk() {
  local ldisk ret
  ldisk=$1
  ret="0"
  if test -b /dev/$ldisk; then
    for i in $(ls /dev/${ldisk}?); do
      unmount_part $(basename $i)
      ret=$(($ret + $?))
    done
  fi
  return $ret 
}

part_fsck() {
  local lpart opts
  lpart=$1
  opts=$2
  if unmount_part $lpart; then
	eval $(blkid -c /dev/null -w /dev/null -s TYPE /dev/$lpart | cut -f2 -d" ") 
	if test "$TYPE" = "ntfs" -a -f /usr/bin/ntfsfix; then
		fsck.ntfs /dev/$lpart
	elif test "$TYPE" = "vfat"; then
		fsck.vfat -a /dev/$lpart
	elif test "${TYPE:0:3}" = "ext"; then
	    e2fsck $opts /dev/$lpart
	fi
    mount /dev/$lpart
    return 0
  else
    return 1
  fi
}

# FIXME if changing filesystem type from/to ext to vfat/ntfs or vice-versa,
# the partition type must be changed too
# also, fstab must be flushed, as labels/partition might have changed

reformat() {
  local lpart ltype
  lpart=$1
  ltype=$2

  if ! unmount_part $lpart; then
	return 1
  fi

  if test "$ltype" = "vfat"; then
    mkfs.vfat /dev/$lpart
  elif test "$ltype" = "ntfs" -a -f /usr/sbin/mkntfs; then
    mkfs.ntfs -q /dev/$lpart
  else
    mke2fs -q -T $ltype /dev/$lpart
  fi

  mkdir -p /mnt/$lpart
  sed -i '\|/dev/'$lpart'|d' /etc/fstab
  echo "/dev/$lpart /mnt/$lpart $ltype defaults 0 0" >> /etc/fstab

  mount /dev/$lpart
  return 0
}

# FIXME - purge fstab (see FIXME above)

newformat() {
  local ldisk ltype lpart lswap
  ldisk=$1
  ltype=$2
  lswap=$3

  if ! unmount_disk $ldisk; then
    return 1
  fi

  if test $lswap = "yes"; then
    ffile="/www/part-swap.fdisk"
    spart=${ldisk}1
    lpart=${ldisk}2
    fdisk /dev/$ldisk <<-EOF
o
n
p
1
1
+512M
n
p
2


t
1
82
w
EOF
  else
    ffile="/www/part.fdisk"
    lpart=${ldisk}1
    fdisk /dev/$ldisk <<-EOF
o
n
p
1


t
83
w
EOF
  fi

#  fdisk /dev/$ldisk < $ffile

  sleep 2 # hotplug is working... how to know it's finish?
  if ! unmount_disk $ldisk; then
    return 1
  fi

  if test $lswap = "yes"; then
    mkswap /dev/$spart
    swapon /dev/$spart
  fi

  reformat $lpart $ltype
  return 0
}

. common.sh
check_cookie
read_args

debug

if test -n "$Clean"; then
  part=$Clean
  opt=$(eval echo "\$opt_$part")
  echo "Clean: part=$part opt="$opt"<br>"	
  part_fsck $part "$opt"

elif test -n "$ReFormat"; then
  part=$ReFormat
  type=$(eval echo "\$type_$ReFormat")
  echo "Reformat: part=$part, type=$type <br>"
  reformat $part $type

elif test -n "$NewFormat"; then
  disk=$NewFormat
  type=$(eval echo "\$type_$NewFormat")
  swap=$(eval echo "\$swap_$NewFormat")
  if test -z "$swap"; then
    swap="no"
  fi
  echo "NewFormat: disk=$disk, type=$type, swap=$swap<br>"
  newformat $disk $type $swap
fi

  echo  "<form action=\"/cgi-bin/disk.cgi\">
	<input type=submit value=\"Continue\"></form></html></body>"

enddebug
#gotopage /cgi-bin/disk.cgi

