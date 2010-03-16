#!/bin/sh

. common.sh
check_cookie
read_args

#if test -z "$NewUser"; then # the gotopage in NewUser
#	debug
#fi

if test -n "$NewUser"; then
	gotopage /cgi-bin/newuser.cgi?uname=$uname

elif test -n "$ChangePass"; then
	gotopage /cgi-bin/newuser.cgi?uname=$uname?nick=$nick

elif test -n "$DelUser"; then
#	echo "Del User: nick=$nick"

	udir=$(awk -F : '/'$nick'/{print $6}' /etc/passwd)
#	rm -rf $(readlink -f "$udir")
	deluser $nick
	rmdir "$udir" >/dev/null 2>&1
	if test $? = 1; then
		msg "The users home directory is not empty and was not deleted"
	fi

elif test -n "$NewGroup"; then
#	echo "Add Group: gname=$gname"
	gname="$(httpd -d "$gname")"
	if test $(eatspaces $gname) != "$gname"; then
		msg "Group name must not contain spaces"
	fi
	eval $(awk -F : '{if ($3 > mg) mg=$3} END{printf "ggid=%d", mg+1}' /etc/group)
	addgroup -g $ggid "$gname"

elif test -n "$DelGroup"; then
#	echo "Del Group: gname=$gname"
	gname="$(httpd -d "$gname")"
	if test $(eatspaces $gname) != "$gname"; then
		msg "Group name must not contain spaces"
	fi
	gid=$(awk -F: -v gname=$gname '$1 == gname {print $3}' /etc/group)
	ug="$(awk -F: -v gid=$gid '$4 == gid {print $1}' /etc/passwd)"
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
		/etc/group
fi

gotopage /cgi-bin/usersgroups.cgi

#enddebug
