#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_HOSTS=/etc/hosts
CONF_MISC=/etc/misc.conf

if test -n "$Submit"; then

	if test -s $CONF_MISC; then 
		. $CONF_MISC
	fi

	net=$(hostname -d 2>/dev/null)
	if test -z "$net"; then net="localnet"; fi

	TF=$(mktemp)
	echo "127.0.0.1	localhost" > $TF
	if test "$MODLOAD_IPV6" = "y"; then
		echo "::1	localhost ipv6-localhost ipv6-loopback"  >> $TF
	fi

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
		elif ! $(checkip $ip); then # FIXME: make checkip() check IPv6 IPs
			msg "The IP must be in the form x.x.x.x, where x is greater than 0 and lower then 255."
		else
			echo "$ip	$nm.$net	$nm" >> $TF
		fi

	done

	mv $TF $CONF_HOSTS
	chmod a+r $CONF_HOSTS

	if rcdnsmasq status >& /dev/null; then
		rcdnsmasq reload >& /dev/null
	fi
fi

#enddebug
gotopage /cgi-bin/hosts.cgi
