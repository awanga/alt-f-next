#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFX=/etc/exports
CONFM=/etc/misc.conf

if test -n "$Submit"; then
	TF=$(mktemp)
	for i in $(seq 1 $((n_exports+3))); do 
		if test -n "$(eval echo \$exp_$i)"; then
			if test -z "$(eval echo \$xopts_$i)"; then
				# keep in sync with nfs.cgi
				eval xopts_$i="rw,no_root_squash,no_subtree_check,anonuid=99,anongid=98"
			fi
			if test -z "$(eval echo \$ip_$i)"; then
				eval ip_$i='*'
			fi

			expd=$(path_escape "$(httpd -d $(eval echo \$exp_$i))")

			httpd -d "$(eval echo \$xcmtd_$i)$expd $(eval echo \"\$ip_$i\")($(eval echo \$xopts_$i))"
			echo
		fi
	done | sort -r > $TF # reverse sort to put commented entries at bottom

	while read share rest; do
		if test -z "$pshare"; then
			echo -n "$share $rest" > $CONFX
		elif test "${share:0:1}" = "#"; then
			echo -e "\n$share $rest" >> $CONFX
		elif test "$share" = "$pshare"; then
			echo -ne " \\\\\n   $rest" >> $CONFX
		else
			echo -ne "\n$share $rest" >> $CONFX
		fi
		pshare=$share
		prest=$rest
	done < $TF
	rm $TF
	echo >> $CONFX

	if rcnfs status >& /dev/null; then
		res="$(exportfs -r 2>&1 )" # exportfs always return 0!
		if test -n "$res"; then
			msg "$res"
		fi
	fi

	sed -i '/^DELAY_NFS=/d;/^CLEAN_STALE_NFS=/d;/^NFS_BLKSIZE=/d' $CONFM

	if test -n "$delay_nfs"; then
		echo DELAY_NFS=y >> $CONFM
	fi

	if test -n "$clean_rmtab"; then
		echo CLEAN_STALE_NFS=y >> $CONFM
	fi

	if test "$NFS_BLKSIZE" != "auto"; then
		echo NFS_BLKSIZE=$NFS_BLKSIZE >> $CONFM
	fi
fi

#enddebug
gotopage /cgi-bin/nfs.cgi


