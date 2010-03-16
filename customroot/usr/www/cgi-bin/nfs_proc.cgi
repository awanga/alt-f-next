#!/bin/sh

. common.sh
check_cookie
read_args

CONFX=/etc/exports
CONFT=/etc/fstab

debug

for i in $(seq 1 $((n_exports+3))); do 
	if test -n "$(eval echo \$exp_$i)"; then
		# printf "%s %s(%s,%s,%s,%s)\n" $(eval echo \$exp_$i \""\$ip_$i"\" \$rd_$i \$mode_$i \$perm_$i \$xopts_$i)
		if test -z "$(eval echo \$xopts_$i)"; then
			eval xopts_$i="no_subtree_check,anonuid=99,anongid=99"
		fi
		if test -z "$(eval echo \$ip_$i)"; then
			eval ip_$i='*'
		fi

		httpd -d "$(eval echo \$xcmtd_$i)$(eval echo \$exp_$i) $(eval echo \"\$ip_$i\")($(eval echo \$rd_$i),$(eval echo \$mode_$i),$(eval echo \$perm_$i),$(eval echo \$xopts_$i))"
		echo
	fi
done  > $CONFX
exportfs -r

sed -i '/ nfs /d' $CONFT

for i in $(seq 1 $((n_fstab+3))); do 
	if test -n "$(eval echo \$rhost_$i)"; then
		#printf "%s:%s\t%s\tnfs\t%s\t0 0\n" $(eval echo \$rhost_$i \$rdir_$i \$mdir_$i \$fopts_$i)
		httpd -d "$(eval echo \$fcmtd_$i)$(eval echo \$rhost_$i):$(eval echo \$rdir_$i) $(eval echo \$mdir_$i) nfs $(eval echo \$fopts_$i) 0 0"
		echo
	fi
done >> $CONFT

echo  "<form action=\"/cgi-bin/nfs.cgi\">
        <input type=submit value=\"Continue\"></form></html></body>
	</body></html>"

#gotopage /cgi-bin/net_services.cgi


