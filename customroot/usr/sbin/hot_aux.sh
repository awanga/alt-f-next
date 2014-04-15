#!/bin/sh

debug=true

if test -n "$debug"; then
	exec >> /var/log/hot_aux.log 2>&1
#	set -x
	echo -e "\nDATE=$(date)"
	env	
fi

# don't do paralell fsck (assume at most one fsck is running)
check() {
	while ls /tmp/check-* >& /dev/null; do
		if kill -0 $(cat /tmp/check-*.pid) 2> /dev/null; then
			echo hot_aux "$MDEV waiting to be fscked"
			sleep 10
		else
			while ! mkdir /tmp/fsck_lock; do sleep 1; done
			rm -f /tmp/check-*
			return
		fi
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

if test -f $MISCC; then . $MISCC; fi

if test "$fsckcmd" != "echo"; then
	
	trap "" 1

	check
	logger -st hot_aux "Start fscking $MDEV"

	xf=/tmp/check-$MDEV
	logf=${xf}.log
	pidf=${xf}.pid

	touch $xf
	echo $$ > $pidf
	rmdir /tmp/fsck_lock 2> /dev/null

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
	logger -st hot_aux "$emsg"
	rm -f $xf $logf $pidf 

	if test -z "$(ls /tmp/check-* 2>/dev/null)"; then
		echo none > $PLED
	fi

else
	logger -st hot_aux "No fsck command for $fstype, $MDEV not fscked."
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
	logger -st hot_aux "Not auto-mounting $lbl as 'noauto' is present in the mount options."
	exit 0
fi

mount $PWD/$MDEV

if test -f /usr/sbin/quotaon; then
	if echo "$mopts" | grep -qE '(grpjquota|usrjquota)'; then
		logger -st hot_aux "Activating quotas on $MDEV"
		quotaon -ug $PWD/$MDEV
	fi
fi

if test -d "/mnt/$lbl/Users"; then
	if ! test -h /home -a -d "$(readlink -f /home)" ; then
		logger -st hot_aux "Users directory found in $lbl"
		ln -s "/mnt/$lbl/Users" /home
	fi
fi

if test -d "/mnt/$lbl/Public"; then
	if ! test -h /Public -a -d "$(readlink -f /Public)" ; then
		logger -st hot_aux "Public directory found in $lbl"
		ln -s "/mnt/$lbl/Public" /Public
	fi
fi

if test -d "/mnt/$lbl/Backup"; then
	if ! test -h /Backup -a -d "$(readlink -f /Backup)" ; then
		logger -st hot_aux "Backup directory found in $lbl"
		ln -s "/mnt/$lbl/Backup" /Backup
	fi
fi

if test -n "$USER_SCRIPT" -a ! -f $USERLOCK; then
	if test "/mnt/$lbl" = "$(dirname $USER_SCRIPT)" -a -x "/mnt/$lbl/$(basename $USER_SCRIPT)"; then
		touch $USERLOCK
		logger -st hot_aux "Executing \"$USER_SCRIPT start\" in background"
		$USER_SCRIPT start &
	fi
fi

if test -d "/mnt/$lbl/ffp"; then
	if ! test -h /ffp -a -d "$(readlink -f /ffp)" ; then
		logger -st hot_aux "ffp directory found in $lbl"
		ln -s "/mnt/$lbl/ffp" /ffp
		if test $? = 0 -a -x /etc/init.d/S??ffp; then
			rcffp start
		fi
	fi
fi

if test -d /mnt/$lbl/Alt-F; then
	if test "$mopts" != "ro"; then
		if ! test -h /Alt-F -a -d "$(readlink -f /Alt-F)"; then
			logger -st hot_aux "Alt-F directory found in $lbl"
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
		logger -st hot_aux "Alt-F directory found in $lbl but not used, as fs is read-only!"
	fi
fi
