#!/bin/sh

. common.sh
check_cookie
read_args

wdir=$(httpd -d "$newdir")
bdir=$(dirname "$wdir")
nbdir=$(echo "$bdir" | sed 's|\([]\&\|[]\)|\\\1|g')

#debug

if test -n "$srcdir"; then
	srcdir=$(httpd -d "$srcdir")
fi

if test -n "$CreateDir"; then
	if test -d "$wdir"; then
		msg "Can't create, folder $wdir already exists."
	elif test -d "$bdir"; then
		res=$(mkdir "$wdir" 2>&1 )
		if test $? != 0; then
			msg "$res"
		fi
	else
		msg "Can't create, parent folder $bdir does not exists."
	fi

elif test -n "$DeleteDir"; then
	if test -d "$wdir"; then
		res=$(rm -rf "$wdir" 2>&1)
		if test $? != 0; then
			msg "$res"
		fi
		HTTP_REFERER=$(echo $HTTP_REFERER | sed -n 's|browse=.*$|browse='"$nbdir"'|p')
	else
		msg "Can't delete, folder $wdir does not exists."
	fi

elif test -n "$Copy" -o -n "$Move" -o -n "$CopyContent"; then
	sbn=$(basename "$srcdir")
	if test -d "${wdir}/${sbn}" -a -z "$CopyContent"; then
		msg "$wdir already contains a folder named $sbn"
	fi

	if test "$op" = "CopyContent"; then
		op="Copy contents"
	fi
	html_header
	wait_count_start "$op from $srcdir to $wdir"

	# cp -a, piped tar and rsync uses too much memory (that keeps growing) for big trees and start swapping
	# cpio has constante memory usage but is limited to 4GB files...
	if test -n "$Copy" -o -n "$CopyContent"; then
		if test -n "$CopyContent"; then
			cd "$srcdir"
			srcdir="."
		else
			cd "$(dirname "$srcdir")"
			srcdir=$(basename "$srcdir")
		fi
		
		tf=$(mktemp -t)
		find "$srcdir" -size +4294967295c > $tf
		if test -s $tf; then
			res=$(find "$srcdir" -depth | grep -v -f $tf | nice cpio -pdm "$wdir" 2>&1)
			st=$?
			if test "$st" = 0; then
				while read fn; do
					td=$(dirname "$fn")
					res=$(nice cp -a "$fn" "$wdir/$td" 2>&1)
					st=$?
					if test "$st" != 0; then break; fi
				done < $tf
			fi	
		else
			res=$(find "$srcdir" -depth | nice cpio -pdm "$wdir" 2>&1)
			st=$?
		fi
		rm -f $tf
	else
		res=$(nice mv -f "$srcdir" "$wdir" 2>&1)
		st=$?
	fi

	wait_count_stop
	if test $st != 0; then
		msg "$res"
	fi
	
	HTTP_REFERER=$(echo $HTTP_REFERER | sed -n 's|browse=.*$|browse='"$nbdir"'|p')
	js_gotopage $HTTP_REFERER
	echo "</body></html>"
	exit 0

elif test -n "$Permissions"; then
	nuser="$(httpd -d $nuser)"
	ngroup="$(httpd -d $ngroup)"
		
	if test -z "$recurse"; then
		optr="-maxdepth 0"
	fi

	if test -z "$toFiles"; then
		optf="-type d"
	fi

	find "$wdir" $optr $optf -exec chown "${nuser}:${ngroup}" {} \;
	find "$wdir" $optr $optf -exec chmod u=$p2$p3$p4,g=$p5$p6$p7,o=$p8$p9$p10 {} \;

	HTTP_REFERER="$(httpd -d $goto)"
fi

#enddebug
gotopage "$HTTP_REFERER"

