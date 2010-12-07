#!/bin/sh

. common.sh
check_cookie
read_args

#debug

wdir="$(httpd -d $newdir)"
bdir="$(dirname "$wdir")"

if test -n "$srcdir"; then
	srcdir="$(httpd -d $srcdir)"
fi

if test -n "$CreateDir"; then
	if test -d "$wdir"; then
		msg "Can't create, directory $wdir already exists."
	elif test -d "$bdir"; then
		res="$(mkdir "$wdir" 2>&1 )"
		if test $? != 0; then
			msg "$res"
		fi
	else
		msg "Can't create, parent directory $bdir does not exist."
	fi

elif test -n "$DeleteDir"; then
	if test -d "$wdir"; then
		res="$(rm -rf "$wdir" 2>&1)"
		if test $? != 0; then
			msg "$res"
		fi
		HTTP_REFERER="$(echo $HTTP_REFERER | sed -n 's|browse=.*$|browse='$bdir'|p')"
	else
		msg "Can't delete, directory $wdir does not exist."
	fi

elif test -n "$Copy" -o -n "$Move"; then
	if test -d "$wdir/$(basename $srcdir)"; then
		msg "$wdir already contains a directory named $(basename $srcdir)"
	fi
	html_header
	wait_count_start "$op from $srcdir to $wdir"
	for i in $(seq 1 5); do sleep 1; echo; done & # why the hell is this needed?!

	if test -n "$Copy"; then
		cmd="cp -a"
	else
		cmd="mv -f"
	fi

	res="$($cmd "$srcdir" "$wdir" 2>&1)"
	st=$?
	wait_count_stop
	if test $st != 0; then
		msg $res
	else
		echo "<p>Success</p> $(back_button) </body></html>"
		exit 0
	fi

elif test -n "$Permissions"; then
	nuser="$(httpd -d $nuser)"
	ngroup="$(httpd -d $ngroup)"
	
	if test -z "$nuser" -o -z "$ngroup"; then
		msg "No user or group for directory?!"
	fi
	
	if test -z "$recurse"; then
		optr="-maxdepth 0"
	fi

	if test -n "$toFiles"; then
		optf="-o -type f"
	fi

	find "$wdir" $optr -type d $optf -exec chown "${nuser}:${ngroup}" {} \;
	find "$wdir" $optr -type d -exec chmod u=$p2$p3$p4,g=$p5$p6$p7,o=$p8$p9$p10 {} \;

	HTTP_REFERER="$(httpd -d $goto)"
fi

#enddebug
gotopage $HTTP_REFERER

exit 0
