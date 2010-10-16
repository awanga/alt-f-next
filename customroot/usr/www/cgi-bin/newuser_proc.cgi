#!/bin/sh

. common.sh
check_cookie
read_args

CONFP=/etc/passwd
CONFR=/etc/rsyncd.conf
CONFRS=/etc/rsyncd.secrets
CONFS=/etc/samba/smbusers

#debug

if test "$submit" = "Submit" -o "$chpass" = "ChangePass"; then
	uname="$(httpd -d "$uname")"
	nick="$(httpd -d "$nick")"

# FIXME add gid support!

	if test "$submit" = "Submit"; then
		ouname="$(awk -F: -v ouname="$uname" '$5 == ouname {print $5}' $CONFP)"
		onick="$(awk -F: -v onick="$nick" '$1 == onick {print $1}' $CONFP)"
		snick="$(echo $nick | tr -d ' ')"

		if test -z "$uname" -o -n "$ouname"; then
			msg "The user name can't be empty or a user with that name already exists"
		elif test -z "$nick" -o -n "$onick" -o "$nick" != "$snick"; then 
			msg "The nickname cant be empty, have spaces, or a user with same nickname already exists"
		elif test -z "$uid" -o "$(awk -F: '$3 == "'$uid'" {print $3}' $CONFP)"; then
			msg "A user with that user id already exists"
		elif test -z "$pass" -o "$pass" != "$passa"; then
			msg "Password can't be empty or does not match"
		fi
		#uname=$(echo "$uname" | tr ' ' '_')
		#adduser -D -G users -u $uid -g "$uname" -h "/home/$nick" $nick > /dev/null 2>&1
		adduser -D -G users -u $uid -g "$uname" -h "/home/$uname" $nick > /dev/null 2>&1
		chmod og-rw "/home/$uname"

		# why doesn't rsync uses unix authorization mechanisms?!
		echo -e "\n[$nick]\npath = /home/$uname\ncomment = $uname home directory\n\
read only = no\nauth users = $nick\nuid = $nick\ngid = users\n" >> $CONFR
	fi

	if test -z "$pass" -o "$pass" != "$passa"; then
		msg "Password can't be empty or does not match"
	fi

	echo "$nick:$pass" | chpasswd > /dev/null 2>&1
	echo -e "$pass\n$pass" | smbpasswd -s -a $nick >& /dev/null
	sed -i "/^$nick = /d" $CONFS  >& /dev/null
	echo "$nick = \"$uname\"" >> $CONFS
	echo -e "username=$nick\npassword=$pass" > /etc/samba/credentials.$nick
	chmod og-rw /etc/samba/credentials.$nick
	sed -i "/^$nick:/d" $CONFRS >& /dev/null
	echo "$nick:$pass" >> $CONFRS
	chmod og-rw $CONFRS

	if test -f /tmp/firstboot; then
		gotopage /cgi-bin/settings.cgi
	else
		gotopage /cgi-bin/usersgroups.cgi
	fi

elif test "$cancel" = "Cancel"; then
	gotopage /cgi-bin/usersgroups.cgi

elif test "$create_dir" = "CreateDir"; then
	if test "$part" = "none"; then
        	msg "You must select a partition"
	fi

	part=/dev/$(httpd -d $part)
	mp="$(awk -v part=$part '$1 == part {print $2}' /proc/mounts)"
	mkdir -p "$mp"/Users
	ln -sf "$mp"/Users /home

	mkdir -p "$mp"/Users/Public

	mkdir -p "$mp"/Users/Public/RO

	mkdir -p "$mp"/Users/Public/RW
	chown nobody:nobody "$mp"/Users/Public/RW
	chmod a+rwx "$mp"/Users/Public/RW

	gotopage /cgi-bin/newuser.cgi
fi

#enddebug

