#!/bin/sh

. common.sh
check_cookie
write_header "Disk Setup -- This is going to change"

s="<strong>"
es="</strong>"
c="<center>"
ec="</center>"

disks=$(ls /dev/sd?) >/dev/null 2>&1

if test -z "$disks"; then
	echo "<br> $s No disks found $es <br>"
	echo "</body></html>"
	exit 1
fi

cat<<-EOF
<h4 align=center> <font color=red>
	WARNING: no further confirmation questions are made!
       <font color=black></h4>

<small>
<p>Disk/partition: Disk name (underlined)/Partition type (partition name)
<p>Cap: Disk or partition capacity
<p>FS: current filesystem on partition
<p>Mtd: Partition is currently mounted
<p>FSCK: Number of mounts to remain until a fsck is done at
  next boot or mount
<p>Dirty: The filesystem is dirty, do an automatic repair OR
  perform a fsck in antecipation and avoid lenghly boot time
<p>New Format: perform an ENTIRE DISK format with the selected filesystem.
  One partition per disk will be created. If Swap  is selected, an aditional
  swap partition will be created (at least one must be present on the box)
<p>Re Format: reformat only the selected partition with the selected filesystem
</small>

<form action="/cgi-bin/disk_proc.cgi" method="post">
EOF

for dsk in $disks; do

	disk=$(basename $dsk)
#  res=$(smartctl -i $dsk) >/dev/null
#  if test $? != 1; then
#	eval $(echo "$res" | awk \
#	    '/^Device Model:/{printf "mod=\"%s %s\";", $3, $4} \
#	     /^Device:/{printf "mod=\"%s %s\";", $2, $3}')
#  else
#	mod="Unknown"
#  fi
	mod=$(cat /sys/block/$disk/device/model)

  fout=$(fdisk -l $dsk | tr '*' ' ') # *: the boot flag...
#	cap=$( echo "$fout" | awk '/Disk/{printf "%.1f", $5/1000000000}')
#	cap=$(expr $(cat /sys/block/$disk/size ) \* 512 / 1000000000)
	cap=$(awk -v sz=$(cat /sys/block/$disk/size) 'BEGIN{printf "%.1f", sz*512/1e9}' /dev/null)

  #disk=$(basename $dsk)
  bay=$(awk '/'$disk'/{print toupper($1)}' /etc/bay)

ntfsopt=""
if test -f /usr/sbin/mkntfs; then
	ntfsopt="<option>ntfs</option>"
fi

cat<<-EOF
	<fieldset><Legend> $s $bay $es ($mod - $cap GB) </legend><table>
	<tr align=center>
	<td> $s <u>Disk</u>/Partition $es </td>
	<td> $s Cap. (GB) $es </td>
	<td> $s FS $es </td>
	<td> $s Mtd $es </td>
	<td> $s FSCK $es </td>
	<td> $s Dirty FS $es </td>
	<td colspan=2> $s New Filesystem $es </td>
	<td> $s Swap $es</td></tr>

    <tr>
    <td align=center> <em> <u> Whole Disk </u></em></td>
    <td align=center> $cap </td>
    <td></td><td></td><td></td><td></td>
    <td><input type=submit name=$disk value="NewFormat"></td>
    <td><select name=type_$disk><option>ext2</option><option>ext3</option><option selected>ext4</option><option>vfat</option>$ntfsopt</select></td>
    <td align=center><input type=checkbox checked name=swap_$disk value="yes"></td>
    </tr>
EOF

  for part in /dev/$disk?; do
    id=""; type="";cap=""
    ppart=$(basename $part)
    curr_fs=$(blkid -s TYPE $part -o value -w /dev/null -c /dev/null )

    eval $(echo "$fout" | awk '/'$ppart'/{printf "id=%s;type=\"%s\";cap=%.1f", \
	$5, substr($0, index($0,$6)), $4*1.024/1000000}')

    mntd=""
    if $(cat /proc/mounts | grep -q $part); then
	mntd="*"
    fi

    clean_dis="disabled"
    font=""
    cnt=""
    fsck_opt="-p"
    if test $id = 83; then
	eval $(tune2fs -l $part 2> /dev/null | awk \
		'/state:/{ if ($3 != "clean") printf "clean_dis=enabled;"} \
		/Mount/{FS=":"; curr_cnt=$2} \
		/Maximum/{FS=":"; max_cnt=$2} \
		END{printf "cnt=%d", max_cnt-curr_cnt}') 
	if test "$cnt" -lt "5" -a "$max_cnt" -gt "0" ; then
		clean_dis=enabled; font="<font color=RED>"; fsck_opt="-fp"
	fi
    fi
clean_dis="enabled" # testing cleaning

    cat<<-EOF
	<tr><td ALIGN=right> $type ($ppart) </td>
	<td ALIGN=right>$cap</td>
	<td align=center> $curr_fs </td>
EOF

    if test $id == 82 -o $id == 5; then
	echo "<td></td><td></td><td></td><td></td><td></td><td></td></tr>"
    else
	cat<<-EOF
    	<td align=center>$mntd</td>
	<td align=center> $font $cnt </td>
	   <input type=hidden name="$fsck_opt" value=opt_$ppart>
        <td><input type=submit $clean_dis name=$ppart value="Clean"></td>
        <td align=right><input type=submit name=$ppart value="ReFormat"></td>
        <td><select name=type_$ppart><option>ext2</option><option>ext3</option><option selected>ext4</option><option>vfat</option>$ntfsopt</select></td>
        <td></td></tr>
EOF
    fi

  done 
	echo "</table></fieldset>"
done

echo "</form></body></html>"
