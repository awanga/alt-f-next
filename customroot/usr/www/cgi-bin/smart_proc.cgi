#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/smartd.conf
CONFO=/etc/misc.conf

mailto() {
	if test -e $CONFO; then
		SENDTO=$(awk -F= '/^MAILTO/{print $2}' $CONFO)
	fi

	if test -z "$SENDTO"; then
		msg "Please setup Mail Settings first"
	fi
}

when() {
	days=""
	for i in $(seq 1 7); do
		if test -n "$(eval echo \$$1_$i)"; then
			days="$days|$(eval echo \$$1_$i)"
		fi
	done
	if test -n "$days"; then
		echo "$2/../../($days)/$(printf "%02d" $3)" | sed 's:(|:(:'
	fi
}

opt="DEVICESCAN -a -d sat -S on"

if test -n "$longtest"; then
	if test -z "$longhour"; then
		msg "You must specify the test starting hour."
	fi
	ldays=$(when l L $longhour)
fi

if test -n "$shorttest"; then
	if test -z "$shorthour"; then
		msg "You must specify the test starting hour."
	fi
	sdays=$(when s S $shorthour)
fi

if test -n "$ldays" -o -n "$sdays"; then
	opt="$opt -s"
	if test -n "$ldays" -a -n "$sdays"; then
		opt="$opt ($ldays|$sdays)"
	elif test -n "$ldays"; then
		opt="$opt $ldays"
	else
		opt="$opt $sdays"
	fi
fi

opt="$opt -m @systemerror.sh,"
if test -n "$mailerror"; then
	mailto
	opt="${opt}$SENDTO"
fi

if test -n "$mailtest"; then
	mailto
	opt="$opt -M test"
fi

if test -n "$offlineauto"; then
	opt="$opt -o on"
fi

if test -n "$wakeup"; then
	opt="$opt -n never"
else
	opt="$opt -n standby"
fi

echo "$opt" > $CONFF

sed -i '/^SMARTD_/d' $CONFO >& /dev/null

echo "SMARTD_INTERVAL=$interval" >> $CONFO

if rcsmart status >& /dev/null; then
	rcsmart reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/sys_services.cgi
