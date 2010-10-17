#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFX=/etc/exports
CONFT=/etc/fstab

if test -n "$unMount"; then
	mp=$(httpd -d "$unMount")
	res="$(umount -f $mp 2>&1)"
	st=$?
	if test $st != 0; then
        msg "Error $st: $res"  
    fi

elif test -n "$Mount"; then
	mp=$(httpd -d "$Mount")
	res="$(mount $mp 2>&1)"
	st=$?
	if test $st != 0; then
        msg "Error $st: $res"  
    fi

elif test -n "$Submit"; then
for i in $(seq 1 $((n_exports+3))); do 
	if test -n "$(eval echo \$exp_$i)"; then
		if test -z "$(eval echo \$xopts_$i)"; then
			# keep in sync with nfs.cgi
			eval xopts_$i="rw,no_root_squash,no_subtree_check,anonuid=99,anongid=98"
			
		fi
		if test -z "$(eval echo \$ip_$i)"; then
			eval ip_$i='*'
		fi

		httpd -d "$(eval echo \$xcmtd_$i)$(eval echo \$exp_$i) $(eval echo \"\$ip_$i\")($(eval echo \$xopts_$i))"
		echo
	fi
done  > $CONFX

res="$(exportfs -r 2>&1 )"
#if test $? != 0; then # exportfs always return 0!
if test -n "$res"; then
	msg "$res"
fi

sed -i '/\(\t\| \)nfs\(\t\| \)/d' $CONFT

for i in $(seq 1 $((n_fstab+3))); do 
	if test -n "$(eval echo \$rhost_$i)"; then
		if test -z "$eval echo \$mopts_$i)"; then
		# keep in sync with nfs.cgi
			mopts_$i= "rw,hard,intr,proto=tcp" # keep in sync with nfs.cgi
		fi
		httpd -d "$(eval echo \$fcmtd_$i)$(eval echo \$rhost_$i):$(eval echo \$rdir_$i) $(eval echo \$mdir_$i) nfs $(eval echo \$mopts_$i) 0 0"
		echo
	fi
done >> $CONFT
fi

#enddebug
gotopage /cgi-bin/nfs.cgi


