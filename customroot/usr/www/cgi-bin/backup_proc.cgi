#!/bin/sh

. common.sh
check_cookie
read_args

CONF=/etc/backup.conf

#debug

if test -n "$BackupNow"; then

	backup $BackupNow &

elif test -n "$Submit"; then

	rm -f $CONF

	dstpath="/Backup"

	for i in $(seq 0 $cnt_know); do
		cmtd=""; type=""; runas=""; srcpath=""; when="";  at=""; log=""; nlogs=""
		id=$i
		cmtd="$(eval echo \$cmtd_$i)"
		type="$(eval echo \$bck_type_$i)"
		runas="$(eval echo \$bck_user_$i)"
		srcpath="$(eval echo \$src_$i)"
		when="$(eval echo \"\$when_$i\")"
		at="$(eval echo \"\$at_$i\")"
		log="$(eval echo \$log_$i)"
		nlogs="$(eval echo \$nlogs_$i)"

		if test -z "$log"; then log=no; fi

		if test -z "$id" -o -z "$type" -o -z "$runas" -o -z "$srcpath" -o -z "$dstpath" \
			-o -z "$when" -o -z "$at" -o -z "$log" -o -z "$nlogs"; then continue; fi

		echo $(httpd -d "${cmtd}$id;$type;$runas;$srcpath;$dstpath;$when;$at;$log;$nlogs") >> $CONF
	done

	if rcbackup status >& /dev/null; then
		rcbackup reload >& /dev/null
	fi

elif test -n "$CreateDir"; then
	if test "$part" = "none"; then
        	msg "You must select a partition"
	fi

	part=/dev/$(httpd -d $part)
	mp="$(awk -v part=$part '$1 == part {print $2}' /proc/mounts)"
	mkdir -p "$mp"/Backup
	chown backup:backup "$mp"/Backup
	chmod g+rwx,o+rx "$mp"/Backup
	ln -sf "$mp"/Backup /Backup
	make_available "[Backup]"
fi

#enddebug
gotopage /cgi-bin/backup.cgi
