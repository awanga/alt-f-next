#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_SMB=/etc/samba/smb.conf

if test "$submit" = "Advanced"; then

	PROTO="http"; PORT=901
	if echo $HTTP_REFERER | grep -q 'https://'; then
		PROTO="https"; PORT=902
	fi
	embed_page "$PROTO://${HTTP_HOST%%:*}:${PORT}" "SWAT Page"

elif test "$submit" = "Submit"; then

	hostdesc=$(httpd -d "$hostdesc")
	workgp=$(httpd -d "$workgp")
	if test -z "$workgp"; then workgp="Workgroup"; fi
	if test -z "$hostdesc"; then hostdesc="DNS-323 NAS"; fi
	sed -i "s/workgroup =.*$/workgroup = $workgp/" $CONF_SMB
	sed -i "s/server string =.*$/server string = $hostdesc/" $CONF_SMB

	cp $CONF_SMB $CONF_SMB-
	awk '
		{ pshare($0) }

		function pshare(line) {
			s = index(line, "[") ; e = index(line, "]")
			share_name = tolower(substr(line, s+1, e-s-1))
			if (share_name == "global" || share_name == "printers") {
				print $0
				while (st = getline) {
					if (substr($0,1,1) == "[")
						break
					printf "%s\n", $0
				}
				if (st == 0)
					exit
			} else
				if (! getline)
					exit
			pshare($0)
		}
	' $CONF_SMB- > $CONF_SMB
	rm $CONF_SMB-

	for i in $(seq 1 $smb_cnt); do
		if test -z "$(eval echo \$ldir_$i)"; then continue; fi

		path=$(httpd -d "$(eval echo \$ldir_$i)")

		shname=$(httpd -d "$(eval echo \$shname_$i)")
		if test -z "$shname"; then shname=$(basename $path); fi

		cmt=$(httpd -d "$(eval echo \$cmt_$i)")
		if test -z "$cmt"; then cmt="$shname folder"; fi

		echo -e "[$shname]"

		echo -e "\tcomment = $cmt"

		echo -e "\tpath = $path"

		user=$(httpd -d "$(eval echo \$user_$i)")
		if test "$user" = "anybody"; then
			echo -e "\tpublic = yes"
		elif test "$user" = "nonpublic"; then
			echo -e "\tpublic = no"
		else
			echo -e "\tvalid users = $user"
		fi

		avail=no
		if test -z "$(eval echo \$avail_$i)"; then
			avail=yes
		fi
		echo -e "\tavailable = $avail"

		if test -z "$(eval echo \$browse_$i)"; then
			echo -e "\tbrowseable = no"
		fi

		ro=yes
		if test -z "$(eval echo \$rdonly_$i)"; then
			ro=no
		fi
		echo -e "\tread only = $ro"

		if test -n "$(eval echo \$inhperms_$i)"; then
			echo -e "\tinherit permissions = yes"
		fi

		echo

	done  >> $CONF_SMB

	if test "$enable_smb2" = yes; then
		sed -i '/max protocol.*SMB2/s/.*/\tmax protocol = SMB2/' $CONF_SMB
	else
		sed -i '/max protocol.*SMB2/s/.*/\t#max protocol = SMB2/' $CONF_SMB
	fi

	if test "$enable_smb1" = yes; then
		sed -i '/min protocol.*SMB2/s/.*/\t#min protocol = SMB2/' $CONF_SMB
	else
		sed -i '/min protocol.*SMB2/s/.*/\tmin protocol = SMB2/' $CONF_SMB
	fi

	if rcsmb status >& /dev/null; then
		rcsmb restart >& /dev/null
	fi	

fi

#enddebug
gotopage /cgi-bin/smb.cgi
