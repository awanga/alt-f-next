#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_RSYNC=/etc/rsyncd.conf

if test "$submit" = "Submit"; then

	awk '{ do {
			if (substr($0,1,1) == "[")
				exit
			printf "%s\n", $0
		} while (st = getline)
	}' $CONF_RSYNC > $CONF_RSYNC-

	for i in $(seq 1 $rsync_cnt); do
		if test -z "$(eval echo \$ldir_$i)" -o -z "$(eval echo \$shname_$i)"; then continue; fi

		httpd -d "$(eval echo -e [\$shname_$i])"; echo
		t=$(httpd -d "$(eval echo comment = \$cmt_$i)"); echo -e "\t$t"
		t=$(httpd -d "$(eval echo path = \$ldir_$i)"); echo -e "\t$t"

		if test -n "$(eval echo \$avail_$i)"; then
			echo -e "\tmax connections = -1"
		fi

		if test -z "$(eval echo \$browse_$i)"; then
			echo -e "\tlist = no"
		fi

		user=$(eval echo \$user_$i)
		if test "$user" != "anybody"; then
			echo -e "\tauth users = $user\n\tuid = $user\n\tgid = $(id -gn $user)"
		fi

		if test -z "$(eval echo \$rdonly_$i)"; then
			echo -e "\tread only = no"
		fi

		echo
	done  >> $CONF_RSYNC-
	mv $CONF_RSYNC- $CONF_RSYNC
fi

#enddebug
gotopage /cgi-bin/inetd.cgi
