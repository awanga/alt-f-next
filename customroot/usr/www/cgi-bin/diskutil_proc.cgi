#!/bin/sh

tune() {
	eval $1
	shift
	eval $2

	while read ln; do
		eval $(echo $ln | awk '/^(\/dev\/sd[a-z]|\/dev\/md[0-9])/{printf "part=%s;type=%s", $1, $3}')
		if test "$type" = "ext2" -o "$type" = "ext3" -o "$type" = "ext4"; then
			tune2fs -c $mounts -i $days $part >& /dev/null
			mounts=$((mounts - 2)) # try to avoid simultaneus fsck at mount time
			days=$((days - 2))
		    fi
	done < /proc/mounts
} 

prog() {
	local dsk tmout
	dsk=/dev/"$1"
	tmout="$2"

	if ! test -b $dsk; then
		return
	fi

	#res=$(hdparm -C $dsk | awk '/drive/{print $4}') >/dev/null 2>&1
	res="$(eval echo \$power_mode_$1)"
	if test "$res" != "standby"; then	
		if test "$tmout" -eq "0"; then
			val=0;
		elif test "$tmout" -le "20"; then
			val=$((tmout * 60 / 5));
		elif test "$tmout" -le "300"; then
			val=$((240 + tmout / 30));
		fi

		/sbin/hdparm -S $val $dsk >/dev/null 2>&1
	fi 	
}

sleepnow() {
	local dsk
	dsk=/dev/$1

	if ! test -b $dsk; then
		return
	fi

	#res=$(hdparm -C $dsk | awk '/drive/{print $4}') >/dev/null 2>&1
	res="$(eval echo \$power_mode_$1)"
	if test "$res" != "standby"; then	
		/sbin/hdparm -y $dsk >/dev/null 2>&1
	fi
}


health() {
	local dsk
	dsk=/dev/$1

	if ! test -b $dsk; then
		return
	fi

	res=$(smartctl -H -i -A -l error -l selftest $dsk)
	html_header
	echo "<pre><small>"
	echo "$res"
	echo  "</small></pre><form action=\"/cgi-bin/diskutil.cgi\">
	<input type=submit value=\"Continue\"></form></html></body>"
}

# dsk op
bay_eject() {
	local bay dsk eop
	dsk=$1
	if test $# = 2; then
		eop=$2
	fi

	bay=$(awk '/'$dsk'/{print $1}' $CONFB)

	if ! test -b "/dev/$dsk"; then
		msg "No valid $dsk disk in $bay bay"
#	elif eject -s $dsk; then 
#		msg "Disk $dsk in $bay bay is not in use, you can safely remove or eject it"
	else
		eject $eop $dsk >/dev/null
		if test -z "$eop" -a $? = 0; then
			msg "You can now remove or eject the $bay device"
		elif test -z "$eop" -a $? = 0; then
			msg "Eject fail, some programs are using the $bay device"
		else
			msg "Filesystems on $bay disk mounted"
		fi
	fi
}

. common.sh

check_cookie
read_args
		    
#debug

CONFF=/etc/hdsleep.conf
CONFT=/etc/tune.conf
CONFB=/etc/bay
CONFTB=/etc/fstab

. /tmp/power_mode

if test "$Submit" = "standby"; then
	while read ln; do
		eval $(echo $ln | awk '/sd[a-z]/{printf "bay=%s;dsk=%s", $1, $2}')
		eval tmout=\$$bay
		sed -i '/^'$bay'/d' $CONFF
		echo "$bay $tmout" >> $CONFF
		prog $dsk $tmout
	done < $CONFB

elif test "$Submit" = "tune"; then
	arg=""
	for i in days mounts; do
		eval val=\$$i
		sed -i '/^'$i'/d' $CONFT
		echo "$i $val" >> $CONFT
		arg="$arg $i=$val"
	done
	tune $arg
  
elif test -n "$StandbyNow"; then
	sleepnow $StandbyNow
	
elif test -n "$Eject"; then
	bay_eject $Eject

elif test -n "$Load"; then
	bay_eject $Load -r

elif test -n "$Status"; then
	health $Status
	exit
else
	debug
fi

#enddebug
gotopage /cgi-bin/diskutil.cgi

