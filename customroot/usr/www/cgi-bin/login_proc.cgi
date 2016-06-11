#!/bin/sh

SECR=/etc/web-secret
TZF=/etc/TZ

. common.sh
read_args

#debug
#set -x

if ! test -s "$SECR"; then
	if test -z "$passwd"; then
		msg "The password can't be empty."
	elif test "$passwd" != "$passwd_again"; then
		msg "The two passwords don't match."
	fi

	if ! passwd=$(checkpass "$passwd"); then
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
		echo host > /tmp/firstboot
		loc="/cgi-bin/host.cgi"
	else
		loc="/cgi-bin/status.cgi"
	fi

elif test "$passwd" = $(cat /etc/web-secret /tmp/salt | md5sum - | cut -d" " -f1); then
	loc="/cgi-bin/status.cgi"
	if test -n "$from_url"; then
		loc=$(httpd -d "$from_url")
	fi
else
	rm -f /tmp/salt
	gotopage /cgi-bin/login.cgi
fi

rm -f /tmp/salt

id=$(uuidgen)
echo $id > /tmp/cookie
chmod og-r /tmp/cookie

echo -e "HTTP/1.1 303\r"
echo -e "Content-Type: text/html\r"
echo -e "Set-Cookie: ALTFID=$id; HttpOnly\r"
echo -e "Location: $loc\r\n\r"

#enddebug
