#!/bin/sh

. common.sh
check_cookie
read_args

CONF=/etc/backup.conf
SMB_CONF=/etc/samba/smb.conf

#debug

if test -n "$Change"; then
	bdir=$(httpd -d "$bdir")
	if ! bdir=$(find_mp "$bdir"); then msg "You have to select a filesystem root"; fi
	if test -d "$bdir/Backup"; then  msg "A folder named $bdir/Backup already exists"; fi

	obdir=$(readlink -f /Backup)
	nbdir=$obdir
	cnt=0
	while test -d $nbdir; do
		nbdir=$obdir-$cnt
		cnt=$((cnt+1))
	done
	mv $obdir $nbdir

	mkdir -p "$bdir"/Backup
	chown backup:backup "$bdir"/Backup
	chmod g+rwx,o+rx "$bdir"/Backup
	rm /Backup
	ln -sf "$bdir"/Backup /Backup

elif test -n "$BackupNow"; then

	backup $BackupNow &

elif test -n "$Submit"; then

	rm -f $CONF

	dstpath="/Backup"

	echo "#id;type;runas;host;mac;srcpath;dstpath;when;at;log;nrotate" > $CONF

	for i in $(seq 0 $cnt_know); do
		cmtd=""; type=""; runas=""; srcpath=""; when="";  at=""; log=""; nlogs=""
		id=$i
		cmtd="$(eval echo \$cmtd_$i)"
		type="$(eval echo \$bck_type_$i)"
		runas="$(eval echo \$bck_user_$i)"
		host="$(eval echo \$host_$i)"
		mac="$(eval echo \$mac_$i)"
		srcpath="$(eval echo \$src_$i)"
		when="$(eval echo \"\$when_$i\")"
		at="$(eval echo \"\$at_$i\")"
		log="$(eval echo \$log_$i)"
		nlogs="$(eval echo \$nlogs_$i)"

		if test -z "$log"; then log=no; fi

		if test -z "$id" -o -z "$type" -o -z "$runas" -o -z "$srcpath" -o -z "$dstpath" \
			-o -z "$when" -o -z "$at" -o -z "$log" -o -z "$nlogs"; then continue; fi

		if test "$type" != "Dir"; then
			if test -z "$host" ; then continue; fi
			if test -z "$mac"; then
				if ping -W 3 -c 2 $host >& /dev/null; then
					res=$(arp -n $host)
					if ! test "$(echo $res | cut -d" " -f1,2,3)" = "No match found"; then
						mac=$(echo $res | cut -d" " -f 4)
					fi
				fi
			fi
		fi

		echo $(httpd -d "${cmtd}$id;$type;$runas;$host;$mac;$srcpath;$dstpath;$when;$at;$log;$nlogs") >> $CONF
	done

	if rcbackup status >& /dev/null; then
		rcbackup reload >& /dev/null
	fi

elif test -n "$CreateDir"; then
	if test "$part" = "none"; then
        	msg "You must select a filesystem"
	fi

	part=/dev/$(httpd -d $part)
	mp="$(awk -v part=$part '$1 == part {print $2}' /proc/mounts)"
	mkdir -p "$mp"/Backup
	chown backup:backup "$mp"/Backup
	chmod g+rwx,o+rx "$mp"/Backup
	ln -sf "$mp"/Backup /Backup

	if ! grep -q "^\[Backup\]" $SMB_CONF; then
		cat<<EOF >> $SMB_CONF

[Backup]
	comment = Backup Area
	path = /Backup
	public = yes
	read only = yes
	available = yes
EOF

		if rcsmb status >& /dev/null; then
			rcsmb reload >& /dev/null
		fi
	fi
fi

#enddebug
gotopage /cgi-bin/backup.cgi
