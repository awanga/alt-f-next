#!/bin/sh

. common.sh
check_cookie
read_args

#debug
#set -x

CONFT=/etc/fstab
CONFM=/etc/misc.conf

start_client() {
	if ! rcnsm status >& /dev/null; then
		rcnsm start >& /dev/null
	fi
}

mkmp() {
	local mp=$1
	if test $(dirname "$mp") != "/mnt"; then
		emsg="$mp is not appropriape for a mount."
	elif ! test -d "$mp"; then
		mkdir -p "$mp"
	fi

	if test -n "$emsg" -a -f $CONFT-; then
		mv $CONFT- $CONFT
		msg "$emsg"
	fi
}

if test -n "$unMount"; then
	start_client
	mp=$(httpd -d "$unMount")
	res="$(umount -f "$mp" 2>&1)"
	st=$?
	if test $st != 0; then
        msg "Error $st: $res"  
    fi

elif test -n "$Mount"; then
	start_client
	mp=$(httpd -d "$Mount")
	mkmp "$mp"
	res=$(mount "$mp" 2>&1)
	st=$?
	if test $st != 0; then
        msg "Error $st: $res"  
    fi

elif test -n "$Submit"; then
	cp $CONFT $CONFT-
	sed -i -e '/\(\t\| \)nfs\(\t\| \)/d' -e '/\(\t\| \)cifs\(\t\| \)/d' $CONFT

	for i in $(seq 1 $cnt); do 
		if test -z "$(eval echo \$rhost_$i)" -o -z "$(eval echo \$rdir_$i)" -o \
			-z "$(eval echo \$mdir_$i)"; then continue; fi

		fstype=$(eval echo \$fstype_$i)
		mopts=$(eval echo \$mopts_$i)
		if test -z "$mopts"; then  # keep in sync with rmount.cgi
			if test $fstype = "nfs"; then
				mopts="rw,hard,intr,proto=tcp,noauto"
			else
				mopts="uid=root,gid=users,credentials=/etc/samba/credentials.root,rw,iocharset=utf8,nounix,noserverino,noauto"
			fi
		fi
		rdir=$(path_escape "$(httpd -d $(eval echo \$rdir_$i))")
		mdir=$(httpd -d $(eval echo \$mdir_$i))
		mkmp "$mdir"
		mdir=$(path_escape "$mdir")

		if test $fstype = "nfs"; then
		httpd -d "$(eval echo \$fcmtd_$i)$(eval echo \$rhost_$i):$rdir $mdir $fstype $mopts 0 0"
		
		else
		httpd -d "$(eval echo \$fcmtd_$i)//$(eval echo \$rhost_$i)/$rdir $mdir $fstype $mopts 0 0"
		fi
		echo
	done >> $CONFT
	
	rm $CONFT-

	sed -i '/^DELAY_NFS=/d' $CONFM

	if test -n "$delay_nfs"; then
		echo DELAY_NFS=y >> $CONFM
	fi

	if rcrmount status >& /dev/null; then
		rcrmount restart >& /dev/null
	fi	

fi

#enddebug
gotopage /cgi-bin/rmount.cgi


