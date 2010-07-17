#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/minidlna.conf

# save old, in case of errors
sed -i 's/^media_dir=.*$/#!#&/' $CONFF

for i in $(seq 1 $cnt); do
	d="$(eval echo \$sdir_$i)"
	if test -z "$d"; then continue; fi
	if test -n "$d"; then
		s=$(httpd -d $d)
		if ! test -d "$s"; then
			sed -i -e '/^!#!media_dir=.*$/d' \
				-e 's/^#!#\(media_dir=.*$\)/\1/' $CONFF
			msg "A directory does not exist."
		fi
		echo "!#!media_dir=$s" >> $CONFF
	fi
done

# sucess, delete old, update new
sed -i -e '/^#!#media_dir=.*$/d' -e 's/^!#!\(media_dir=.*$\)/\1/' $CONFF

rcminidlna status >& /dev/null
if test $? = 0; then
	rcushare force-reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

