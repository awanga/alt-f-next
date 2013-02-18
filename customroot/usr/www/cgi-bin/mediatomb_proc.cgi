#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/var/lib/mediatomb/config.xml

if test -n "$webPage"; then
	embed_page "http://${HTTP_HOST%%:*}:50500" "MediaTomb Page"
fi

# save old, in case of errors
sed -i '/<directory .*$/s/^.*$/#!#&/' $CONFF

for i in $(seq 1 $cnt); do
	d="$(eval echo \$sdir_$i)"
	if test -z "$d"; then continue; fi
	if test -n "$d"; then
		s=$(httpd -d "$d")
		if ! test -d "$s"; then
			sed -i -e '/^!#!.*<directory .*$/d' \
				-e 's/^#!#\(.*<directory .*$\)/\1/' $CONFF
			msg "A directory does not exist."
		fi
		sed -i '/<autoscan>/a \
!#!      \<directory location=\"'"$s"'\" mode=\"inotify\" recursive=\"yes\"/\>' $CONFF
	fi
done

# sucess, delete old, update new
sed -i -e '/^#!#.*<directory .*$/d' -e 's/^!#!\(.*<directory .*$\)/\1/' $CONFF

if test -z "$ENABLE_WEB"; then ENABLE_WEB="no"; fi
sed -i 's/<ui enabled=.*>/<ui enabled="'$ENABLE_WEB'" show-tooltips="yes">/' $CONFF

if test -z "$sname"; then
	sname=MediaTomb
else
	sname=$(httpd -d "$sname")
fi
sed -i 's|<name>.*</name>|<name>'"$sname"'</name>|' $CONFF

rcmediatomb status >& /dev/null
if test $? = 0; then
	rcmediatomb reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

