#!/bin/sh

# $1=HDSLEEP_* | HDPOWER_* $2=val
prog() {
	local dsk tmout
	dsk=$(grep -i ${1#*_}_dev /etc/bay | cut -d"=" -f2)
	act=${1%_*}
	op="$2"

	if test -z "$dsk" -o ! -b /dev/$dsk; then
		return
	fi

	case $act in
		HDSLEEP)
			if test "$op" -eq "0"; then
				tmout=0;
			elif test "$op" -le "20"; then
				tmout=$((op * 60 / 5));
			elif test "$op" -le "300"; then
				tmout=$((240 + op / 30));
			fi
			hdparm -S $tmout /dev/$dsk >& /dev/null
			;;
		HDPOWER)
			hdparm -B $op /dev/$dsk >& /dev/null
			;;
	esac
}

sleepnow() {
	local dsk
	dsk=/dev/$1

	if ! test -b $dsk; then
		return
	fi

	if test "$(disk_power $1)" != "standby"; then	
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

# $1=dsk $2=op
bay_eject() {
	local bay dsk eop
	dsk=$1
	if test $# = 2; then
		eop=$2
	fi

	disk_details $1

	eject $eop $dsk >/dev/null
	if test -z "$eop" -a $? = 0; then
		msg "You can now remove or eject the $dbay device"
	elif test -z "$eop" -a $? != 0; then
		msg "Eject fail, some programs are using the $dbay device"
	else
		msg "Filesystems on $dbay disk mounted"
	fi
}

. common.sh

check_cookie
read_args
		    
#debug

CONFT=/etc/misc.conf

if test -n "$StandbyNow"; then
	sleepnow $StandbyNow

elif test -n "$WakeupNow"; then
	blkid -c /dev/null /dev/${WakeupNow}* >& /dev/null
	
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

# this must the last else. Currently HDPOWER_* is always visible
elif test -n "$standby" -o -n "$HDPOWER_LEFT" -o -n "$HDPOWER_RIGHT" -o -n "$HDPOWER_USB"; then
	for i in HDPOWER_LEFT HDPOWER_RIGHT HDPOWER_USB HDSLEEP_LEFT HDSLEEP_RIGHT HDSLEEP_USB; do
		if test -n "$(eval echo \$$i)"; then
			sed -i '/^'$i'/d' $CONFT >& /dev/null
			echo "$i=$(eval echo \$$i)" >> $CONFT
			prog $i $(eval echo \$$i)
		fi
	done
fi

#enddebug
gotopage /cgi-bin/diskutil.cgi

