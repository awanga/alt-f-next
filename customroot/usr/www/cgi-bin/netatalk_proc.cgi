#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_NETA=/etc/afp.conf

if test "$submit" = "Submit"; then

	if test -n "$dhx2"; then
		uml="uams_dhx2.so"
	fi

	if test -n "$dhx"; then
		uml="$uml uams_dhx.so"
	fi

	if test -n "$clrtxt"; then
		uml="$uml uams_clrtxt.so"
	fi

	if test -n "$allow_guest"; then
		uml="$uml uams_guest.so"
	fi

	sed -i "s/^[[:space:]]*uam list[[:space:]]*=.*/\tuam list = $uml/" $CONF_NETA

	if grep -q '^\[Homes\]' $CONF_NETA; then
		has_homes="yes"
	fi

	if test -n "$want_homes" -a -z "$has_homes" ; then
		echo -e "[Homes]\n\tbasedir regex = $(realpath /home)\n" >> $CONF_NETA
	fi

	if test -z "$want_homes" -a -n "$has_homes" ; then
		sed -i '/^\[Homes\]/,/^\[.*\]/ {/^\[Homes\]/d;/^\[.*\]/ !d}' $CONF_NETA
	fi

	cp $CONF_NETA $CONF_NETA-
	awk '
		{ pshare($0) }

		function pshare(line) {
			s = index(line, "[") ; e = index(line, "]")
			share_name = substr(line, s+1, e-s-1)
			if (share_name == "Global" || share_name == "Homes") {
				print $0
				while (st = getline) {
					if (substr($0,1,1) == "[")
						break
					printf "%s\n", $0
				}
				if (st == 0)
					exit
			} else {
				if (! getline)
					exit
			}
			pshare($0)
		}
	' $CONF_NETA- > $CONF_NETA

	for i in $(seq 1 $neta_cnt); do
		if test -z "$(eval echo \$ldir_$i)"; then continue; fi

		path=$(httpd -d "$(eval echo \$ldir_$i)")

		shname=$(httpd -d "$(eval echo \$shname_$i)")
		if test -z "$shname"; then shname="$(basename $path) Share"; fi
		echo -e "[$shname]"

		echo -e "\tpath = $path"

		user=$(httpd -d "$(eval echo \$user_$i)")
		if test -n "$user" -a "$user" != "anybody"; then
			echo -e "\tvalid users = $user"
		fi

		if test -n "$(eval echo \$rdonly_$i)"; then
			echo -e "\tread only = yes"
		fi

		if test -n "$(eval echo \$tm_$i)"; then
			echo -e "\ttime machine = yes"
		fi

		maxsz=$(httpd -d "$(eval echo \$maxsz_$i)")
		if test -n "$maxsz"; then
			echo -e "\tvol size limit = $maxsz"
		fi

		echo

	done  >> $CONF_NETA

	if rcnetatalk status >& /dev/null; then
		rcnetatalk reload >& /dev/null
	fi	

fi

#enddebug
gotopage /cgi-bin/netatalk.cgi
