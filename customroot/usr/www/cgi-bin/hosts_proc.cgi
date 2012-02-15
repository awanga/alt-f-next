#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_HOSTS=/etc/hosts

if test -n "$Submit"; then

	TF=$(mktemp)
	net=$(hostname -d)
	echo -e "127.0.0.1	localhost\n::1	localhost ipv6-localhost ipv6-loopback"  > $TF

	for i in $(seq 0 $cnt_know); do
		nm=$(eval echo \$knm_$i)
		ip=$(eval echo \$kip_$i)

		if test -z "$nm" -a -z "$ip"; then continue; fi

		if test -z "$nm" -o -z "$ip"; then
			rm $TF
			msg "You must specify a name and IP."
		fi

		ip=$(httpd -d $ip)

		if ! $(checkname $nm); then
			rm $TF
			msg "The host name can only have letters and digits, no spaces, and must begin with a letter"
		fi

		if echo "$ip" | grep -q ':'; then
			echo "$ip	$nm" >> $TF
		elif ! $(checkip $ip); then
			msg "The IP must be in the form x.x.x.x, where x is greater than 0 and lower then 255."
		else
			echo "$ip	$nm.$net	$nm" >> $TF
		fi

	done

	mv $TF $CONF_HOSTS

	if rcdnsmasq status >& /dev/null; then
		rcdnsmasq reload >& /dev/null
	fi
fi

#enddebug
gotopage /cgi-bin/hosts.cgi
