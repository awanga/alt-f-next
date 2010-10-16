#!/bin/sh

. common.sh
check_cookie
read_args

CONFP=/etc/passwd
CONFG=/etc/group
CONFS=/etc/samba/smbusers
CONFR=/etc/rsyncd.conf
CONFRS=/etc/rsyncd.secrets

#if test -z "$NewUser"; then # the gotopage in NewUser
#	debug
#fi

if test -n "$NewUser"; then
	gotopage /cgi-bin/newuser.cgi?uname=$uname

elif test -n "$ChangePass"; then
	gotopage /cgi-bin/newuser.cgi?uname=$uname?nick=$nick

elif test -n "$DelUser"; then
#	echo "Del User: nick=$nick"

	udir=$(awk -F : '/'$nick'/{print $6}' $CONFP)
#	rm -rf $(readlink -f "$udir")
	smbpasswd -x $nick >& /dev/null
	rm -f /etc/samba/credentials.$nick
	sed -i "/^$nick = /d" $CONFS >& /dev/null
	sed -i "/^$nick:/d" $CONFRS  >& /dev/null
	sed -i "/^\[$nick\]/,/^$/d" $CONFR
	
	deluser $nick
	if test -d "$udir"; then
		rmdir "$udir" >& /dev/null
		if test $? = 1; then
			msg "The users home directory is not empty and was not deleted"
		fi
	fi

elif test -n "$NewGroup"; then
#	echo "Add Group: gname=$gname"
	gname="$(httpd -d "$gname")"
	if test $(eatspaces $gname) != "$gname"; then
		msg "Group name must not contain spaces"
	fi
	eval $(awk -F : '{if ($3 > mg) mg=$3} END{printf "ggid=%d", mg+1}' $CONFG)
	addgroup -g $ggid "$gname"

elif test -n "$DelGroup"; then
#	echo "Del Group: gname=$gname"
	gname="$(httpd -d "$gname")"
	if test $(eatspaces $gname) != "$gname"; then
		msg "Group name must not contain spaces"
	fi
	gid=$(awk -F: -v gname=$gname '$1 == gname {print $3}' $CONFG)
	ug="$(awk -F: -v gid=$gid '$4 == gid {print $1}' $CONFP)"
	if test -n "$ug"; then
		msg "This group is the main group of several users, can't delete it"
	fi
	delgroup "$gname"

elif test -n "$AddToGroup"; then
#	echo "Add user to Group: gname=$gname nick=$nick"
	addgroup $nick "$gname"

elif test -n "$DelFromGroup"; then
#	echo "Del user from Group: gname=$gname nick=$nick"		

	# delgroup $nick $gname # not working, busybox bug
	sed -i  -e '/^'$gname':/s/,'$nick'$//'  \
		-e '/^'$gname':/s/:'$nick',/:/' \
		-e '/^'$gname':/s/,'$nick',/,/' \
		-e '/^'$gname':/s/:'$nick'$/:/'  \
		$CONFG
fi

gotopage /cgi-bin/usersgroups.cgi

#enddebug
