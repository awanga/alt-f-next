#!/bin/sh

SECR=/etc/web-secret
TZF=/etc/TZ

. common.sh
read_args

#debug

if ! test -e $SECR; then
	if test -z "$passwd"; then
		msg "The password can't be empty."
	elif test "$passwd" != "$passwd_again"; then
		msg "The two passwords don't match."
	fi

	passwd=$(checkpass $passwd)
	if test $? != 0; then
    	msg "$passwd"
	fi

	echo -n $passwd > $SECR
	chmod og-r $SECR
# FIXME: if root already has a password, don't change it?
	echo "root:$passwd" | chpasswd > /dev/null 2>&1

	echo -e "username=Administrator\npassword=$passwd" > /etc/samba/credentials.root
	chmod og-rw /etc/samba/credentials.root
	if ! grep -q '^root = ' /etc/samba/smbusers 2>/dev/null; then
		echo "root = \"Administrator\"" >> /etc/samba/smbusers
	fi
	echo -e "$passwd\n$passwd" | smbpasswd -s -a root >& /dev/null

	sed -i '/root/d' /etc/rsyncd.secrets
	echo -e "root:$passwd" >> /etc/rsyncd.secrets

	if test -z "$(loadsave_settings -ls)"; then
		touch /tmp/firstboot
		loc="/cgi-bin/host.cgi"
	else
		loc="/cgi-bin/status.cgi"
	fi
else
	passwd=$(checkpass $passwd)
	if test $? != 0; then
    	msg "$passwd"
	fi

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

	cat<<-EOF
		HTTP/1.1 303
		Content-Type: text/html
		Set-Cookie: ALTFID=$id;
		Location: $loc

	EOF
else
	gotopage /cgi-bin/login.cgi
fi

#enddebug
