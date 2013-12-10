#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONF_FSTAB=/etc/fstab
CONF_SMB=/etc/samba/smb.conf

if test -n "$unMount"; then
	mp=$(httpd -d "$unMount")
	res="$(umount "$mp" 2>&1)"
	st=$?
	if test $st != 0; then
		msg "Error $st: $res"
	fi

elif test -n "$Mount"; then
	mp=$(httpd -d "$Mount")
	res="$(mount "$mp" 2>&1)"
	st=$?
	# /etc/mtab is a link to /proc/mounts, mount.cifs cant lock it
	if test $st != 0 -a $st != 16; then 
		msg "Error $st: $res"
	fi

elif test "$submit" = "Submit"; then

	cp $CONF_FSTAB $CONF_FSTAB-
	sed -i '/\(\t\| \)cifs\(\t\| \)/d' $CONF_FSTAB

	for i in $(seq 1 $import_cnt); do
		if test -z "$(eval echo \$rhost_$i)" -o -z "$(eval echo \$rdir_$i)" -o \
			-z "$(eval echo \$mdir_$i)" -o -z "$(eval echo \$mopts_$i)"; then continue; fi

		rdir=$(path_escape "$(httpd -d $(eval echo \$rdir_$i))")
		mdir=$(httpd -d $(eval echo \$mdir_$i))
		if test ! -d "$mdir" -o "$mdir" = "/mnt"; then
			fstab_err=1
			break
		fi
		mdir=$(path_escape "$mdir")

		httpd -d "$(eval echo \$fstab_en_${i}//\$rhost_${i}/\"$rdir $mdir\" cifs \$mopts_$i 0 0)"
		echo
	done  >> $CONF_FSTAB

	if test -n "$fstab_err"; then
		mv $CONF_FSTAB- $CONF_FSTAB
		msg "\"$mdir\" is not a folder or is inappropriate for a mount point."
	else
		rm $CONF_FSTAB-
	fi

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

	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi	

fi

#enddebug
gotopage /cgi-bin/smb.cgi
