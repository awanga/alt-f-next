#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_AFPD=/etc/netatalk/afpd.conf
CONF_AVOL=/etc/netatalk/AppleVolumes.default

sed -i '/\(^\/\|^"\/\|^~\|^:DEFAULT:\)/d' $CONF_AVOL

if test -n "$def_opts"; then
	echo ":DEFAULT: $(httpd -d $(eval echo \$def_opts))" >> $CONF_AVOL
fi

for i in $(seq 0 $afpd_cnt); do
	if test -z "$(eval echo \$ldir_$i)" -o -z "$(eval echo \$shname_$i)"; then
		continue
	fi

	opts=$(httpd -d "$(eval echo \$opts_$i)")
	if test -z "$opts"; then
		opts=""
	fi

	ldir=$(httpd -d "$(eval echo \$ldir_$i)")
	shname=$(httpd -d "$(eval echo \$shname_$i)")

	echo -e "\"$ldir\"\t\"$shname\"\t$opts"

done  >> $CONF_AVOL

if test "$user_en" = "yes"; then
	echo "~" >> $CONF_AVOL
fi

if rcafpd status >& /dev/null; then
	rcafpd reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/afpd.cgi
