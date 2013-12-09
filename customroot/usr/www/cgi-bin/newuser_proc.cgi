#!/bin/sh

. common.sh
check_cookie
read_args

CONFP=/etc/passwd
CONFR=/etc/rsyncd.conf
CONFRS=/etc/rsyncd.secrets
CONFS=/etc/samba/smbusers
CONFSMB=/etc/samba/smb.conf

#debug

if test "$submit" = "Submit" -o "$chpass" = "ChangePass"; then
	uname="$(httpd -d "$uname")"
	nick="$(httpd -d "$nick")"
	if test -n "$(echo $nick | tr -d [:alnum:])"; then
		msg "The nick name \'$nick\' has illegal characters,\n only letters and digits are allowed."
	fi

	if test -z "$pass" -o -z "$passa"; then
		msg "The passwords can't be empty"
	fi

	if test "$pass" != "$passa"; then
		msg "The passwords does not match"
	fi

	pass=$(checkpass "$pass")
	if test $? != 0; then
		msg "$pass"
	fi

	passa=$(checkpass "$passa")
	if test $? != 0; then
		msg "$passa"
	fi

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
		fi
		if test "$gid" != 100; then
			addgroup -g $gid $nick >& /dev/null
			grp="-G $nick"
		else
			grp="-G users"
		fi
		res=$(adduser -D $grp -u $uid -g "$uname" -h "/home/$uname" $nick 2>&1)
		if test $? != 0; then
			msg "$res"
		fi
		chmod og-rw "/home/$uname"
		chown -R $nick:$gid "/home/$uname"
		addgroup $nick backup

		# why doesn't rsync uses unix authorization mechanisms?!
		echo -e "\n[$nick]\n\tpath = /home/$uname\n\tcomment = $uname home folder\n\
\tread only = no\n\tauth users = $nick\n\tuid = $nick\n\tgid = users\n" >> $CONFR
		echo -e "\n[$uname]\n\tpath = /home/$uname\n\tcomment = $uname home folder\n\
\tread only = no\n\tauth users = $nick\n\tuid = $nick\n\tgid = users\n" >> $CONFR
	fi

	echo "$nick:$pass" | chpasswd > /dev/null 2>&1
	echo -e "$pass\n$pass" | smbpasswd -s -a $nick >& /dev/null
	sed -i "/^$nick = /d" $CONFS  >& /dev/null
	echo "$nick = \"$uname\"" >> $CONFS
	echo -e "username=$uname\npassword=$pass" > /etc/samba/credentials.$nick
	chmod og-rw /etc/samba/credentials.$nick
	sed -i "/^$nick:/d" $CONFRS >& /dev/null
	echo "$nick:$pass" >> $CONFRS
	echo "$uname:$pass" >> $CONFRS
	chmod og-rw $CONFRS

	gotopage /cgi-bin/usersgroups.cgi

elif test "$cancel" = "Cancel"; then
	gotopage /cgi-bin/usersgroups.cgi

elif test "$create_dir" = "CreateDir"; then
	if test "$part" = "none"; then
        msg "You must select a filesystem"
	fi

	part=/dev/$(httpd -d $part)
	mp="$(awk -v part=$part '$1 == part {print $2}' /proc/mounts)"
	mkdir -p "$mp"/Users
	ln -sf "$mp"/Users /home

	mkdir -p "$mp"/Public
	chmod a-w "$mp"/Public
	ln -sf "$mp"/Public /Public

	mkdir -p "$mp"/Public/RO
	mkdir -p "$mp"/Public/RW
	chown nobody:nobody "$mp"/Public/RW
	chmod a+rwx "$mp"/Public/RW

	OIFS="$IFS"; IFS=":"
	while read  nick x uid gid name hdir rest; do
		if echo "$nick" | grep -q '^#'; then continue; fi
		if test "$uid" -ge 1000; then
			if ! test -d "$hdir"; then
				mkdir "$hdir"
				chown $nick:$gid "$hdir"
			fi
		fi
	done < $CONFP
	IFS="$OIFS"

	if ! grep -q "^\[Users\]" $CONFSMB; then
		cat<<EOF >> $CONFSMB		

[Users]
	comment = Users private folder
	path = /home
	read only = no
	available = yes
			
[Public (Read Write)]
	comment = Public Area where everybody can read and write
	inherit permissions = yes
	path = /Public/RW
	public = yes
	read only = no
	available = yes
		
[Public (Read Only)]
	comment = Public Area that everybody can read
	path = /Public/RO
	public = yes
	read only = yes
	available = yes
EOF

		if rcsmb status >& /dev/null; then
			rcsmb reload >& /dev/null
		fi
	fi

	gotopage /cgi-bin/$(basename "$HTTP_REFERER")
fi

#enddebug

