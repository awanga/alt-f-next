#!/bin/sh

prog() {
	local dsk tmout
	dsk=$(grep -i ${1#*_} /etc/bay | cut -d" " -f2)
	tmout="$2"

	if ! test -b /dev/$dsk; then
		return
	fi

	res="$(eval echo \$power_mode_$dsk)"
	if test "$res" != "standby"; then	
		if test "$tmout" -eq "0"; then
			val=0;
		elif test "$tmout" -le "20"; then
			val=$((tmout * 60 / 5));
		elif test "$tmout" -le "300"; then
			val=$((240 + tmout / 30));
		fi

		/sbin/hdparm -S $val /dev/$dsk >/dev/null 2>&1
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
	echo  "</small></pre>$(back_button)</html></body>"
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

CONFT=/etc/misc.conf
CONFB=/etc/bay
CONFTB=/etc/fstab

. /tmp/power_mode

if test "$Submit" = "standby"; then
	for i in HDSLEEP_LEFT HDSLEEP_RIGHT HDSLEEP_USB; do
		if test -n "$(eval echo \$$i)"; then
			sed -i '/^'$i'/d' $CONFT >& /dev/null
			echo "$i=$(eval echo \$$i)" >> $CONFT
			prog $i $(eval echo \$$i)
		fi
	done
  
elif test -n "$StandbyNow"; then
	sleepnow $StandbyNow

elif test -n "$WakeupNow"; then
	blkid -c /dev/null /dev/$WakeupNow >& /dev/null
	
elif test -n "$Eject"; then
	bay_eject $Eject

elif test -n "$Load"; then
	bay_eject $Load -r

elif test -n "$hstatus"; then
	health $hstatus
	exit

elif test -n "$shorttest"; then
	res="$(smartctl -t short /dev/$shorttest)"
	res="$(echo $res | sed -n 's/.*successful\.\(.*\)Use.*/\1/p')"
	msg "$res\n\nYou can see the result using Health Status."

elif test -n "$longtest"; then
	res="$(smartctl -t long /dev/$longtest)"
	res="$(echo $res | sed -n 's/.*successful\.\(.*\)Use.*/\1/p')"
	msg "$res\n\nYou can see the result using Health Status."
fi

#enddebug
gotopage /cgi-bin/diskutil.cgi

