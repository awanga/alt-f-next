#!/bin/sh

debug=true

if test -n "$debug"; then
	exec >> /var/log/hot_aux.log 2>&1
#	set -x
	echo -e "\nDATE=$(date)"
	env	
fi

check() {
	if test "${MDEV:0:2}" = "md"; then
		we=$(ls /sys/block/$MDEV/slaves/ | tr -d [0-9]'\n' | \
			sed -n 's/\(...\)\(...\)/\(\1\|\2\)/p')
	else
		we=${MDEV:0:3}
	fi

	while true; do
		inuse=""
		inclean=$(ls /tmp/check-sd[a-z][1-9] /tmp/check-md[0-9] 2> /dev/null | grep -oE '(sd[a-z].|md[0-9])')
		if test -z "$inclean"; then break; fi
		for i in "$inclean"; do
			if test "${i:0:2}" = "md"; then
				inuse="$inuse $(ls /sys/block/$i/slaves)"
			else
				inuse="$inuse $i"
			fi
		done

		if ! echo "$inuse" | grep -q -E "$we"; then
			break
		fi
		logger -t hot_aux "$MDEV waiting to be fscked"
		sleep 10
	done
}

MISCC=/etc/misc.conf
FSTAB=/etc/fstab
USERLOCK=/var/lock/userscript
SERRORL=/var/log/systemerror.log
PLED=/tmp/sys/power_led/trigger

fsckcmd=$1
fsopt=$2
mopts=$3
lbl=$4
fstype=$5

if test -f $MISCC; then
	. $MISCC
fi

if test "$fsckcmd" != "echo"; then
	
	trap "" 1

	check
	logger -t hot_aux "Start fscking $MDEV"

	xf=/tmp/check-$MDEV
	logf=${xf}.log
	pidf=${xf}.pid

	touch $xf
	echo $$ > $pidf 

	if test "$fsopt" = "-"; then
		fsopt=""
	fi

	echo heartbeat > $PLED
	res="$($fsckcmd $fsopt -C5 $PWD/$MDEV 2>&1 5<> $logf)"
	if test $? -ge 2; then
		mopts="ro"
		emsg="Unable to automatically fix $MDEV, mounting Read Only: $res"
		echo "<li><pre>$emsg</pre>" >> $SERRORL
	else
		emsg="Finish fscking $MDEV: $res"
	fi
	logger -t hot_aux "$emsg"
	rm -f $xf $logf $pidf 

	if test -z "$(ls /tmp/check-* 2>/dev/null)"; then
		echo none > $PLED
	fi

else
	logger -t hot_aux "No fsck command for $fstype, $MDEV not fscked."
fi

# record fstab date, don't change it
touch -r /etc/fstab /tmp/fstab_date
# concurrency: this needs a lock
while ! mkdir /tmp/fstab_lock >& /dev/null; do sleep 1; done
sed -i '\|^'$PWD/$MDEV'|d' $FSTAB
echo "$PWD/$MDEV /mnt/$lbl $fstype $mopts 0 0" >> $FSTAB
rmdir /tmp/fstab_lock
touch -r /tmp/fstab_date /etc/fstab
rm /tmp/fstab_date

# don't mount if noauto is present in mount options
if echo "$mopts" | grep -q noauto; then
	logger -t hot_aux "Not auto-mounting $lbl as 'noauto' is present in the mount options."
	exit 0
fi

mount $PWD/$MDEV

if test -f /usr/sbin/quotaon; then
	if echo "$mopts" | grep -qE '(grpjquota|usrjquota)'; then
		logger -t hot_aux "Activating quotas on $MDEV"
		quotaon -ug $PWD/$MDEV
	fi
fi

if test -f "/mnt/$lbl/alt-f.fail"; then
	rm -f "/mnt/$lbl/alt-f.fail"
fi

if test -d "/mnt/$lbl/Users"; then
	if ! test -h /home -a -d "$(readlink -f /home)" ; then
		logger -t hot_aux "Users directory found in $lbl"
		ln -s "/mnt/$lbl/Users" /home
	fi
fi

if test -d "/mnt/$lbl/Public"; then
	if ! test -h /Public -a -d "$(readlink -f /Public)" ; then
		logger -t hot_aux "Public directory found in $lbl"
		ln -s "/mnt/$lbl/Public" /Public
	fi
fi

if test -d "/mnt/$lbl/Backup"; then
	if ! test -h /Backup -a -d "$(readlink -f /Backup)" ; then
		logger -t hot_aux "Backup directory found in $lbl"
		ln -s "/mnt/$lbl/Backup" /Backup
	fi
fi

if test -n "$USER_SCRIPT" -a ! -f $USERLOCK; then
	if test "/mnt/$lbl" = "$(dirname $USER_SCRIPT)" -a -x "/mnt/$lbl/$(basename $USER_SCRIPT)"; then
		touch $USERLOCK
		logger -t hot_aux "Executing \"$USER_SCRIPT start\" in background"
		$USER_SCRIPT start &
	fi
fi

if test -d "/mnt/$lbl/ffp"; then
	if ! test -h /ffp -a -d "$(readlink -f /ffp)" ; then
		logger -t hot_aux "ffp directory found in $lbl"
		ln -s "/mnt/$lbl/ffp" /ffp
		if test $? = 0 -a -x /etc/init.d/S??ffp; then
				/etc/init.d/S??ffp start
		fi
	fi
fi

if test -d /mnt/$lbl/Alt-F; then
	if test "$mopts" != "ro"; then
		if ! test -h /Alt-F -a -d "$(readlink -f /Alt-F)"; then
			logger -t hot_aux "Alt-F directory found in $lbl"
			rm -f /mnt/$lbl/Alt-F/Alt-F /mnt/$lbl/Alt-F/ffp /mnt/$lbl/Alt-F/home
			ln -s /mnt/$lbl/Alt-F /Alt-F
			echo "DON'T ADD, REMOVE OR MODIFY ANY FILE IN THIS DIRECTORY
OR ANY OF ITS SUB-DIRECTORIES, OR THE SYSTEM MIGHT HANG!" > /Alt-F/README.txt
			for i in /Alt-F/etc/init.d/S??*; do
				f=$(basename $i)
				ln -sf /usr/sbin/rcscript /sbin/rc${f#S??}
				if test -x $i; then
					tostart="$tostart rc${f#S??}"
				fi
			done
			if test -n "$DELAY_NFS" -a -x /etc/init.d/S60nfs; then
				tostart="$tostart rcnfs"
			fi
			aufs.sh -m
			for i in $tostart; do
				logger -st hot_aux "$($i start)"
			done
		fi
	else
		logger -t hot_aux "Alt-F directory found in $lbl but not used, as fs is read-only!"
	fi
fi
