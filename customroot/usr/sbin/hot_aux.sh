#!/bin/sh

debug=true

if test -n "$debug"; then
	exec >> /var/log/hot_aux.log 2>&1
#	set -x
	echo -e "\nDATE=$(date)"
	env
fi

MISCC=/etc/misc.conf
FSTAB=/etc/fstab
USERLOCK=/var/lock/userscript
SERRORL=/var/log/systemerror.log
PLED=/tmp/sys/power_led/trigger

if test -f $MISCC; then . $MISCC; fi

# don't do paralell fsck (assume at most one fsck is running)
check() {
	while ls /tmp/check-* >& /dev/null; do
		if kill -0 $(cat /tmp/check-*.pid) 2> /dev/null; then
			# is it being checked? lvm generates extra events...
			if test -f /tmp/check-$MDEV; then exit 0; fi
			echo hot_aux "$MDEV waiting to be fscked"
			sleep 10
		else
			while ! mkdir /tmp/fsck_lock; do sleep 1; done
			rm -f /tmp/check-*
			return
		fi
	done
}

start_altf_dir() {
	if test -d /mnt/$lbl/Alt-F; then
		if test -f /mnt/$lbl/Alt-F/NOAUFS; then
			emsg="Alt-F directory found in $lbl but not used, as file NOAUFS exists on it."
			logger -st hot_aux $emsg
			echo "<li>$emsg</li>" >> $SERRORL
		elif test "$mopts" != "ro"; then
			if ! test -h /Alt-F -a -d "$(readlink -f /Alt-F)"; then
				logger -st hot_aux "Alt-F directory found in $lbl"
				for i in Alt-F ffp home Public Backup; do
					if test -h /mnt/$lbl/Alt-F/$i; then
						rm -f /mnt/$lbl/Alt-F/$i
					fi
				done
				ln -s /mnt/$lbl/Alt-F /Alt-F
				echo "DON'T ADD, REMOVE OR MODIFY ANY FILE UNDER /ALT-F or $(realpath /Alt-F 2> /dev/null)
	OR ANY OF ITS SUB-DIRECTORIES, OR THE SYSTEM MIGHT HANG!" > /Alt-F/README.txt
				for i in $(ls /Alt-F/etc/init.d/S??* 2> /dev/null); do
					f=$(basename $i)
					ln -sf /usr/sbin/rcscript /sbin/rc${f#S??}
					if test -x $i; then
						tostart="$tostart rc${f#S??}"
					fi
				done

				if test -n "$DELAY_NFS"; then
					snfs="/etc/init.d/S61nfs /etc/init.d/S69rmount"
				fi

				for i in $snfs $(grep -l "^NEED_ALTF_DIR=1" /etc/init.d/S??*); do
					if test -x $i; then
						f=$(basename $i)
						tostart="$tostart rc${f#S??}"
					fi
				done

				# the existence of spool on disk prevents it to spindown,
				# so use /tmp/var/spool for all spooling, not preserving data across reboots.
				if test -d /Alt-F/var/spool; then
					rm -rf /Alt-F/var/spool-old
					mv /Alt-F/var/spool /Alt-F/var/spool-old
				fi

				if ! aufs.sh -m; then
					emsg="Alt-F directory found in $lbl but not used, aufs mount failed."
					logger -st hot_aux $emsg
					echo "<li>$emsg</li>" >> $SERRORL
					return 1
				fi

				ipkg -update # >& /dev/null # force ipkg_upgrade to update packages

				for i in $tostart; do
					if ! test -f /sbin/$i; then # ipkg_upgrade might have removed them
						ln -sf /usr/sbin/rcscript /sbin/$i
					fi
					logger -st hot_aux "$($i restart)"
				done
			fi
		else
			emsg="Alt-F directory found in $lbl but not used, as filesystem is read-only!"
			logger -st hot_aux $emsg
			echo "<li>$emsg</li>" >> $SERRORL
		fi
	fi
}

stop_altf_dir() {
	if test -d /mnt/$lbl/Alt-F -a "$(readlink -f /Alt-F 2> /dev/null)" = "/mnt/$lbl/Alt-F"; then

		for i in $(ls -r /Alt-F/etc/init.d/S??*); do
			f=$(basename $i)
			f=rc${f#S??}
			if $f status >& /dev/null; then
				tostop="$tostop $f"
			fi
		done

		for i in $(grep -l "^NEED_ALTF_DIR=1" /etc/init.d/S??* | sort -r); do
			f=$(basename $i)
			f=rc${f#S??}
			if $f status >& /dev/null; then
				tostop="$tostop $f"
			fi
		done

		for i in $tostop; do
			logger -st hot_aux "$($i stop)"
		done

		for i in $(ls /Alt-F/etc/init.d/S??* 2> /dev/null); do
			f=$(basename $i)
			if ! test -f /etc/init.d/$f; then
				f=rc${f#S??}
				rm -f /sbin/$f
			fi
		done

		if ! aufs.sh -u; then
			logger -st hot_aux "aufs.sh unmount failed"
			start_altf_dir
			return 1
		fi
		
		rm  -f /Alt-F
	fi
}

if test "$1" = "-start-altf-dir"; then
	lbl=$(basename $(dirname $2))
	mopts="$(awk '$1 == "/dev/'$lbl'" { n = split($4, a,",")
		for (i=1;i<=n;i++) {
			if (a[i] == "ro") {
				printf "%s", a[i]; exit }
		}
	} ' /proc/mounts)"
	logger -st hot_aux -start-altf-dir lbl="$lbl" mopts="$mopts"
	start_altf_dir
	exit $?

elif test "$1" = "-stop-altf-dir"; then
	lbl=$(basename $(dirname $2))
	logger -st hot_aux -stop-altf-dir lbl="$lbl"
	stop_altf_dir
	exit $?

elif test "$#" != 5 -o -z "$MDEV"; then
	exit $?
fi

fsckcmd=$1
fsopt=$2
mopts=$3
lbl=$4
fstype=$5

if test "$fsckcmd" != "echo"; then
	
	trap "" 1

	check

	if test "$fsopt" = "-"; then fsopt=""; fi

# FIXME: /tmp/fsckboot has to be removed, or most ops from Disk->Filesystem
# will be done twice, as hot.sh is called at its end.
# Is that a good place to remove it, when the user checks a fs?
	if test -f /tmp/fsckboot && echo $fstype | grep -q 'ext.' ; then
		fsopt="-fp"
		cmsg="force"
	fi

	logger -st hot_aux "Start $cmsg fscking $MDEV"

	xf=/tmp/check-$MDEV
	logf=${xf}.log
	pidf=${xf}.pid

	touch $xf
	echo $$ > $pidf
	rmdir /tmp/fsck_lock 2> /dev/null

	echo heartbeat > $PLED
if true; then
	mkfifo /tmp/fsck_pipe-$MDEV >& /dev/null
	# create pipe consumer background job
	(while true; do
		dd if=/tmp/fsck_pipe-$MDEV of=$logf- bs=64K count=1 2> /dev/null 
		mv $logf- $logf
		sleep 5
	done)&
	wj=$!
	res="$($fsckcmd $fsopt -C5 $PWD/$MDEV 2>&1 5<> /tmp/fsck_pipe-$MDEV)"
else
	res="$($fsckcmd $fsopt -C5 $PWD/$MDEV 2>&1 5<> $logf)"
fi
	if test $? -ge 2; then
		mopts="ro"
		emsg="Unable to automatically fix $MDEV, mounting Read Only: $res"
		echo "<li><pre>$emsg</pre></li>" >> $SERRORL
	else
		emsg="Finish fscking $MDEV: $res"
	fi
	logger -st hot_aux "$emsg"
if true; then
	kill $wj
	#echo > /tmp/fsck_pipe-$MDEV # echo blocks here!
	rm -f /tmp/fsck_pipe-$MDEV $logf- 
fi
	rm -f $xf $logf $pidf

	if test -z "$(ls /tmp/check-* 2>/dev/null)"; then
		echo none > $PLED
	fi

else
	emsg="No fsck command for $fstype, $MDEV not fscked."
	logger -st hot_aux $emsg
	echo "<li>$emsg</li>" >> $SERRORL
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
	emsg="Not auto-mounting $lbl as 'noauto' is present in the mount options."
	logger -st hot_aux $emsg
	echo "<li>$emsg</li>" >> $SERRORL
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
		find /home/ -maxdepth 2 -name crontab.lst | while read ln; do
			dname=$(dirname "$ln")
			cd "$dname"
			duid=$(stat -t . | cut -d " " -f5)
			fuid=$(stat -t crontab.lst | cut -d " " -f5)
			if test $duid != $fuid; then continue; fi
			user=$(ls -l crontab.lst | awk '{print $3}')
			logger -st hot_aux "Starting crontab for $user"
			crontab -u $user crontab.lst
		done
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

if test -d "/mnt/$lbl/ffp"; then
	if ! test -h /ffp -a -d "$(readlink -f /ffp)" ; then
		logger -st hot_aux "ffp directory found in $lbl"
		ln -s "/mnt/$lbl/ffp" /ffp
		if test $? = 0 -a -x /etc/init.d/S??ffp; then
			rcffp start
		fi
	fi
fi

start_altf_dir

# the user script might need the Alt-F dir aufs mounted, so run it last
if test -n "$USER_SCRIPT" -a ! -f $USERLOCK; then
	if test "/mnt/$lbl" = "$(dirname $USER_SCRIPT)" -a -x "/mnt/$lbl/$(basename $USER_SCRIPT)"; then
		touch $USERLOCK
		logger -st hot_aux "Executing \"$USER_SCRIPT start\" in background"
		$USER_SCRIPT start &
	fi
fi

