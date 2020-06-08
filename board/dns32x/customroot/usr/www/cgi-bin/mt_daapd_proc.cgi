#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/mt-daapd.conf
DEF_DIR=/var/lib/mt-daapd/mp3_dir

if test -n "$webPage"; then
	PORT=$(awk '/^port/{print $2}' $CONFF)
	webhost="${HTTP_HOST%%:*}:$PORT"
	embed_page "http://$webhost" "mt-daapd Page" # defaul is mt-daapd:mt-daapd
fi

if test "$def_dir" = "yes"; then
	rm -f $DEF_DIR/*

	for i in $(seq 1 $cnt); do
		d="$(eval echo \$sdir_$i)"
		if test -z "$d"; then continue; fi
		if ! test -d "$(httpd -d $d)"; then
			msg "At least one directory does not exists."
		fi
		s=$(httpd -d $d)
		n=$(basename "$s")
		t=$(mktemp -p $DEF_DIR "$n"-XXXXXX)
		ln -sf "$s" "$t"
	done
	sed -i 's|^servername.*|servername '"$(httpd -d $sname)"'|' $CONFF
else
	share="$(httpd -d $sdir_1)"
	sed -i 's|^mp3_dir.*$|mp3_dir '"$share"'|' $CONFF
fi

if rcmt_daapd status >& /dev/null; then
	rcmt_daapd restart >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi
