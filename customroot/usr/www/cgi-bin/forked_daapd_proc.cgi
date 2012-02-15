#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_FORKED=/etc/forked-daapd.conf

for i in $(seq 1 $cnt); do
	d="$(eval echo \$sdir_$i)"
	if test -z "$d"; then continue; fi
	if ! test -d "$(httpd -d $d)"; then
		msg "At least one directory does not exists."
	fi
	res="\"$d\",$res"
done

shares="$(httpd -d $res)"
sed -i -e 's|directories =.*$|directories = { '"$shares"' } |' -e 's/, }/ }/' $CONF_FORKED

sname="$(httpd -d $sname)"
sed -i 's|\tname =.*$|\tname = "'"$sname"'"|' $CONF_FORKED 

if rcforked_daapd status >& /dev/null; then
	rcforked_daapd restart >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

