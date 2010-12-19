#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/smartd.conf
CONFM=/etc/msmtprc
CONFO=/etc/misc.conf

mailto() {
	if test -e $CONFM; then
		SENDTO=$(awk '/^from/{ print $2}' $CONFM)
	fi

	if test -z "$SENDTO"; then
		msg "Please setup Mail Settings first"
	fi
}

when() {
	days="("
	for i in $(seq 1 7); do
		##if test -n "$(eval echo \$$1_$i)"; then
			days="$days|$(eval echo \$$1_$i)"
		##fi
	done
	echo "$days)"
}

opt="DEVICESCAN -a -d sat -S on"

if test -n "$longtest"; then
	if test -z "$longhour"; then
		msg "You must specify the test starting hour."
	fi
	ldays="L/../../$(when l)/$(printf "%02d" $longhour)"
fi

if test -n "$shorttest"; then
	if test -z "$shorthour"; then
		msg "You must specify the test starting hour."
	fi
	sdays="S/../../$(when s)/$(printf "%02d" $shorthour)"
fi

if test -n "$longtest" -o -n "$shorttest"; then
	opt="$opt -s ($ldays|$sdays)"
fi

if test -n "$mailerror"; then
	mailto
	opt="$opt -m $SENDTO"
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
