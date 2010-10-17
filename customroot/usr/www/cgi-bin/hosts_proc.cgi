#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_HOSTS=/etc/hosts

if test -n "$Submit"; then

	net=$(hostname -d)
	echo "127.0.0.1	localhost" > $CONF_HOSTS

	for i in $(seq 0 $cnt_know); do
		nm=$(eval echo \$knm_$i)
		ip=$(eval echo \$kip_$i)

		if test -z "$nm" -a -z "$ip"; then continue; fi

		if test -z "$nm" -o -z "$ip"; then
			msg "You must specify a name and IP."
		fi
		if ! $(checkname $nm); then
			msg "The host name can only have letters and digits, no spaces, and must begin with a letter"
		elif ! $(checkip $ip); then
			msg "The IP must be in the form x.x.x.x, where x is greater than 0 and lower then 255."
		fi

		echo "$ip	$nm.$net	$nm" >> $CONF_HOSTS
	done
fi

#enddebug
gotopage /cgi-bin/hosts.cgi
