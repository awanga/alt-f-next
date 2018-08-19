#!/bin/sh

m2g() {
    if test "$1" -ge 1000; then
		echo $1 | awk '{printf "%.1fGB", $1/1000}'
    else
        echo "${1}MB"
    fi
}

. common.sh
check_cookie
read_args

LOCAL_STYLE='
#ellapsed {
	position: relative;
	z-index: -1;  
	margin-left: auto;
	margin-right: auto;
	width: 33%;
	font-size: 1.5em;
}
'

wdir=$(httpd -d "$newdir")
wdir=$(echo "$wdir" | sed -n 's/^ *//;s/ *$//p')
bdir=$(dirname "$wdir")
nbdir=$(url_encode "$bdir")

#debug
#set -x

if ! echo "$wdir" | grep -q '^/mnt'; then
	msg "Only operations on /mnt sub-folders are allowed."
fi

if test -n "$srcdir"; then
	srcdir=$(httpd -d "$srcdir")
fi

if test -n "$oldname"; then
	oldname=$(httpd -d "$oldname")
fi

if test -n "$CreateDir"; then
	if test -d "$wdir"; then
		msg "Can't create, folder\n\n   $wdir\n\nalready exists."
	elif test -d "$bdir"; then
		res=$(mkdir "$wdir" 2>&1 )
		if test $? != 0; then
			msg "Creating failed:\n\n $res"
		fi
		HTTP_REFERER=$(echo "$HTTP_REFERER" | sed "s|?browse=.*|?browse=$newdir|")
	else
		msg "Can't create, parent folder\n\n   $bdir\n\ndoes not exists."
	fi
	
elif test -n "$RenameDir"; then
	if test "$oldname" = "$wdir"; then
		msg "The new and old names are identical."
	fi

	if ! test -d "$oldname"; then
		msg "Can't rename, folder\n\n   $oldname\n\ndoesn't exists."
	fi

	if test -d "$wdir"; then
		msg "Can't rename, folder\n\n   $wdir\n\nalready exists."
	fi
	
	if ! test -d "$bdir"; then
		msg "Can't rename, parent folder\n\n   $bdir\n\ndoesn't exists."
	fi

	bname=$(dirname "$oldname")
	if test "$bdir" != "$bname"; then
		msg "Can't rename, parent folders must be the same, use Cut/Paste instead."
	fi

	res=$(mv "$oldname" "$wdir" 2>&1)
	if test $? != 0; then
		msg "Renaming failed:\n\n $res"
	fi
	HTTP_REFERER=$(echo "$HTTP_REFERER" | sed "s|?browse=.*|?browse=$newdir|")

elif test -n "$DeleteDir"; then
	if ! test -d "$wdir"; then
		msg "Can't delete, folder\n\n   $wdir\n\ndoes not exists."
	fi

	src_sz=$(du -sm "$wdir" | cut -f1)
	terr=$(mktemp -t)

	html_header "Deleting $(m2g $src_sz) \"$wdir\" folder"
	cat<<-EOF
		<div id="ellapsed"></div>
	EOF

	busy_cursor_start
	nice rm -rf "$wdir" 2> $terr &

	bpid=$!
	touch /tmp/folders_op.$bpid
	sleep_time=$(expr \( $src_sz / 10000 + 1 \) \* 100000)
	if test "$sleep_time" -gt 2000000; then sleep_time=2000000; fi
	while kill -0 $bpid >& /dev/null; do
		usleep $sleep_time
		rm_sz=$(du -sm "$wdir" 2>/dev/null | cut -f1)
		if test -z "$rm_sz" -o "$src_sz" = 0; then continue; fi
		el=$(expr $rm_sz \* 100 / $src_sz)
		cat<<-EOF
		<script type="text/javascript">
			document.getElementById("ellapsed").innerHTML = '$(drawbargraph $el $(m2g $rm_sz) | tr "\n" " " )';
		</script>
		EOF
	done
	wait $bpid
	st=$?

	busy_cursor_end

	rm -f /tmp/folders_op.$bpid
	res=$(cat $terr)
	rm -f $terr
	if test $st != 0; then
		msg "Deleting failed:\n\n $res"
	fi

	HTTP_REFERER=$(echo "$HTTP_REFERER" | sed 's|?browse=.*$|?browse='"$nbdir"'|')
	js_gotopage "$HTTP_REFERER"

elif test -n "$Copy" -o -n "$Move" -o -n "$CopyContent"; then
	if ! test -d "$srcdir"; then
		msg "Failed, folder\n\n   $srcdir\n\n does not exists."
	fi

	sbn=$(basename "$srcdir")
	if test -d "${wdir}/${sbn}" -a -z "$CopyContent"; then
		msg "Failed, folder\n\n $wdir\n\n already contains a folder named\n\n   $sbn"
	fi

	src_mp=$(find_mp "$srcdir")
	src_sz=$(du -sm "$srcdir" | cut -f1)

	dst_mp=$(find_mp "$wdir")
	dst_free=$(df -m $dst_mp | awk '/\/mnt\//{print $4}')

	if test "$op" = "CopyContent"; then
		op="Copy Contents"
	fi

	if test -n "$Copy" -o -n "$CopyContent"; then
		if test $src_sz -gt $dst_free; then
			msg "Can't $op, $(m2g $src_sz) needed and only $(m2g $dst_free) are available."
		fi
	elif test $src_mp != dst_mp; then
		if test $src_sz -gt $dst_free; then
			msg "Can't $op, $(m2g $src_sz) needed and only $(m2g $dst_free) are available."
		fi
	fi

	terr=$(mktemp -t)

	html_header "$op $(m2g $src_sz) from \"$srcdir\" to \"$wdir\""
	if test -n "$CopyContent"; then
		echo "<p class=\"warn\">Displayed values are incorrect if files being copied already exists in the destination folder</p>"
	fi
	echo "<div id=\"ellapsed\"></div>"
	busy_cursor_start

	exist_sz=0
	if test -n "$Copy" -o -n "$CopyContent"; then
		if test -n "$CopyContent"; then
			cd "$srcdir"
			srcdir="."
			exist_sz=$(du -sm "$wdir" | cut -f1)
		else
			cd "$(dirname "$srcdir")"
			srcdir=$(basename "$srcdir")
		fi
		cmd="cp -a \"$srcdir\" \"$wdir\""
	else
		cmd="mv -f \"$srcdir\" \"$wdir\" 2> $terr"
	fi

	eval $cmd &
	bpid=$!

	touch /tmp/folders_op.$bpid
	td="$wdir/$(basename "$srcdir")"
	# FIXME: not suitable to TB operations, don't limit it, use an exponential waiting time
	sleep_time=$(expr $src_sz / 100 + 1) 
	if test $sleep_time -gt 10; then sleep_time=10; fi
		cat<<-EOF
		<script type="text/javascript">
			document.getElementById("ellapsed").innerHTML = '$(drawbargraph 1 0MB | tr "\n" " " )';
		</script>
		EOF
	while kill -0 $bpid >& /dev/null; do
		sleep $sleep_time
		if test ! -d "$td" -o "$src_sz" = 0; then continue; fi
		curr_sz=$(nice du -sm "$td" | cut -f1)
		mv_sz=$((curr_sz - exist_sz))
		el=$((mv_sz * 100 / src_sz))
		cat<<-EOF
		<script type="text/javascript">
			document.getElementById("ellapsed").innerHTML = '$(drawbargraph $el $(m2g $mv_sz) | tr "\n" " " )';
		</script>
		EOF
	done
	wait $bpid
	st=$?

	busy_cursor_end

	rm -f /tmp/folders_op.$bpid
	res=$(cat $terr)
	rm -f $terr

	if test $st != 0; then
		msg "Failed:\n\n$res"
	fi

	js_gotopage "$HTTP_REFERER"

elif test -n "$Permissions"; then
	nuser="$(httpd -d $nuser)"
	ngroup="$(httpd -d $ngroup)"
		
	if test -z "$recurse"; then
		optr="-maxdepth 0"
	fi

	if test -z "$toFiles"; then
		optf="-type d"
	fi

	if test -n "$setgid"; then
		setgid="s"
	fi

	find "$wdir" $optr $optf -exec chown "${nuser}:${ngroup}" {} \;
	find "$wdir" $optr $optf -exec chmod u=$p2$p3$p4,g=$p5$p6$p7$setgid,o=$p8$p9$p10 {} \;

	HTTP_REFERER=$(httpd -d "$goto")
fi

#enddebug
gotopage "$HTTP_REFERER"

