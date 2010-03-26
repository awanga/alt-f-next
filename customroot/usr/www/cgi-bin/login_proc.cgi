#!/bin/sh

SECR=/etc/web-secret
TZF=/etc/TZ

. common.sh
read_args

#debug

if ! test -e $SECR; then
	if test "$passwd" != "$passwd_again"; then
		gotopage /cgi-bin/login.cgi
	fi

	echo -n $passwd > $SECR
	chmod og-r $SECR
	echo "root:$passwd" | chpasswd > /dev/null 2>&1
	touch /tmp/firstboot
	loc="/cgi-bin/host.cgi"
else
	if test "$from_url" != "login.cgi"; then
		loc="/cgi-bin/$from_url"
	else
		loc="/cgi-bin/status.cgi"
	fi
fi

if test "$passwd" = "$(cat $SECR)"; then
	id=$(uuidgen)
	echo $id > /tmp/cookie
	chmod og-r /tmp/cookie
    
	if test $(cat $TZF) = "NONE-0"; then
		expl=""
	else
		eval $(TZ=GMT awk 'END{printf "exp=%s", \
			strftime("\"%a, %d-%b-%Y %T GMT\"", systime()+3600)}' /dev/null)
		expl="expires=$exp"
	fi
    
	cat<<-EOF
		HTTP/1.1 303
		Content-Type: text/html
		Set-Cookie: ALTFID=$id; $expl
		Location: $loc

	EOF
else
	gotopage /cgi-bin/login.cgi
fi

#enddebug
