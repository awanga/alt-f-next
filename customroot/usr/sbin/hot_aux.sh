#!/bin/sh

exec >> /var/log/hot_aux.log 2>&1
set -x

check() {
	if test "${MDEV:0:2}" = "md"; then
		we=$(ls /sys/block/$MDEV/slaves/ | tr -d [0-9]'\n' | \
			sed -n 's/\(...\)\(...\)/\(\1\|\2\)/p')
	else
		we=${MDEV:0:3}
	fi

	while true; do
		inuse=""
		inclean=$(ls /tmp/clean-* | sed 's|/tmp/clean-||')
		for i in $inclean; do
			if test ${i:0:2} = "md"; then
				inuse="$inuse $(ls /sys/block/$i/slaves)"
			else
				inuse="$inuse $i"
			fi
		done

		if ! echo $inuse | grep -q -E "$we"; then
			return 0
		fi
		logger -t hot "$MDEV waiting to be fscked"
		sleep 10
	done
}

FSTAB=/etc/fstab

fsckcmd=$1
fsopt=$2
mopts=$3
lbl=$4
fstype=$5

if test "$fsckcmd" != "echo"; then
	
	trap "" 1

	check
	logger -t hot "Start fscking $MDEV"

	xf=/tmp/clean-$MDEV
	logf=${xf}.log
	pidf=${xf}.pid

	touch $xf
	echo $$ > $pidf 

	if test "$fsopt" = "-"; then
		fsopt=""
	fi

	# echo heartbeat > "/sys/class/leds/power:blue/trigger"
	res="$($fsckcmd $fsopt -C5 $PWD/$MDEV 2>&1 5<> $logf)"
	if test $? -ge 2; then mopts="ro"; fi
	logger -t hot "Stop fscking $MDEV: $res"
	# echo none > "/sys/class/leds/power:blue/trigger"

	rm -f $xf $logf $pidf 
else
	logger -t hot "No fsck command for $fstype, $MDEV not fscked."
fi

# concurrency: this needs a lock?
sed -i '\|^'$PWD/$MDEV'|d' $FSTAB
echo "$PWD/$MDEV /mnt/$lbl $fstype $mopts 0 0" >> $FSTAB

mount $PWD/$MDEV

if test -f "/mnt/$lbl/alt-f.fail"; then
	rm -f "/mnt/$lbl/alt-f.fail"
fi

if test -d "/mnt/$lbl/Users"; then
	if ! test -h /home -a -d "$(readlink -f /home)" ; then
		ln -s "/mnt/$lbl/Users" /home
	fi
fi

if test -d "/mnt/$lbl/Public"; then
	if ! test -h /Public -a -d "$(readlink -f /Public)" ; then
		ln -s "/mnt/$lbl/Public" /Public
	fi
fi

if test -d "/mnt/$lbl/Backup"; then
	if ! test -h /Backup -a -d "$(readlink -f /Backup)" ; then
		ln -s "/mnt/$lbl/Backup" /Backup
	fi
fi

if test -d "/mnt/$lbl/ffp"; then
	if ! test -h /ffp -a -d "$(readlink -f /ffp)" ; then
		ln -s "/mnt/$lbl/ffp" /ffp
		if test $? = 0 -a -x /etc/init.d/S??ffp; then
				/etc/init.d/S??ffp start
		fi
	fi
fi

if test -d /mnt/$lbl/Alt-F; then
	if ! test -h /Alt-F -a -d "$(readlink -f /Alt-F)"; then
		rm -f /mnt/$lbl/Alt-F/Alt-F /mnt/$lbl/Alt-F/ffp /mnt/$lbl/Alt-F/home
		ln -s /mnt/$lbl/Alt-F /Alt-F
		echo "DONT'T ADD, REMOVE OR CHANGE ANY FILE ON THIS DIRECTORY
OR IN ANY OF ITS SUBDIRECTORIES, OR THE SYSTEM MIGHT HANG." > /Alt-F/README.txt
		for i in /Alt-F/etc/init.d/S??*; do
			f=$(basename $i)
			ln -sf /usr/sbin/rcscript /sbin/rc${f#S??}
		done
		loadsave_settings -ta
		mount -t aufs -o remount,prepend:/mnt/$lbl/Alt-F=rw /
	fi
fi

