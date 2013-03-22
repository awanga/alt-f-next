#!/bin/sh

. common.sh
check_cookie
read_args

kernel_file="/tmp/kernel"
initramfs_file="/tmp/initramfs"
defaults_file="/tmp/defaults"

if test "$flash" = "Abort"; then
	rm $kernel_file $initramfs_file $defaults_file > /dev/null 2>&1
	gotopage /cgi-bin/firmware.cgi
fi

# $1-file, $2-device, $3-msg
flash() {
	sz=$(stat -t $1 | cut -d" " -f2)
	tm=$(expr $sz / 75126 + 1)
	wait_count_start "<p>Flashing the $3, it takes about $tm seconds"
	cat $1 > /dev/$2
	wait_count_stop
	echo "<p>Verifying..."
	TF=$(mktemp)
	# make sure that next read (dd) is from flash, not cache
	sync
	echo 3 > /proc/sys/vm/drop_caches
	echo 3 > /proc/sys/vm/drop_caches
	dd if=/dev/$2 of=$TF bs=$sz count=1 >& /dev/null
	if ! cmp $1 $TF >& /dev/null; then
		rm -f $TF $kernel_file $initramfs_file $defaults_file
		echo none > "/sys/class/leds/power:blue/trigger"
		echo "Failed!<p>You can use the Firmware Upgrade page to try again, or \"TryIt\" another firmware, but<br><strong><font color=red>don't reboot or poweroff the box until success</font></strong><br> or you will need to buy and solder a serial cable into the box to make it work again.</body></html>"
		exit 1
	fi
	echo "OK"
	rm $TF
}

html_header "Firmware Updater"

if ! test -f $kernel_file -a -f $initramfs_file; then
	rm -f $kernel_file $initramfs_file $defaults_file
	cat<<-EOF
		<br>
		<form action="/cgi-bin/firmware.cgi" method="post">
		Kernel and/or ramdisk file missing <input type="submit" value="Retry">
		</form></body></html>
	EOF
	exit 0
fi

if test "$flash_defaults" = "flash" -a ! -s $defaults_file; then
	rm -f $kernel_file $initramfs_file $defaults_file
	cat<<-EOF
		<br>
		<form action="/cgi-bin/firmware.cgi" method="post">
		defaults file missing or empty <input type="submit" value="Retry">
		</form></body></html>
	EOF
	exit 0
fi

if test "$flash" = "SpecialReboot"; then
	rm -f $initramfs_file $kernel_file $defaults_file
	dd if=/dev/mtdblock2 of=/root/zImage bs=64 skip=1 >& /dev/null
	dd if=/dev/mtdblock3 of=/root/rootfs.arm.sqmtd bs=64 skip=1 >& /dev/null

elif test "$flash" = "TryIt"; then
	dd if=$kernel_file of=/root/zImage bs=64 skip=1 >& /dev/null
	dd if=$initramfs_file of=/root/rootfs.arm.sqmtd bs=64 skip=1 >& /dev/null
	rm -f $initramfs_file $kernel_file $defaults_file

elif test "$flash" = "FlashIt"; then
	echo "<center><h3><font color=red>Don't poweroff or reboot the box!</font></h3></center>"
	rcall stop >& /dev/null

	echo timer > "/sys/class/leds/power:blue/trigger"
	echo 50 > "/sys/class/leds/power:blue/delay_off" 
	echo 50 > "/sys/class/leds/power:blue/delay_on"

	flash $kernel_file mtdblock2 kernel
	flash $initramfs_file mtdblock3 rootfs

	case "$flash_defaults" in
		"none")
			;;

		"clear")
			echo "<p>Erasing flashed settings, it takes some 5 seconds..."
			loadsave_settings -cf
			;;

		"flashfile")
			echo "<p>Flashing new settings, it takes some 5 seconds..."
			mkdir /tmp/mtd
			mount /dev/mtdblock0 /tmp/mtd
			rm -f /tmp/mtd/*
			tar -C /tmp -xzf $defaults_file
			cp -f /tmp/default/* /tmp/mtd/
			umount /tmp/mtd
			rmdir /tmp/mtd
			rm -rf /tmp/default
			;;

		"recover")
			echo "<p>Recovering vendors settings from backup, it takes some 5 seconds..."
			loadsave_settings -rc
			;;
	esac

	rm -f $kernel_file $initramfs_file $defaults_file
	echo none > "/sys/class/leds/power:blue/trigger"
fi

cat<<-EOF
	<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
	You can continue using the current firmware,<br>
	but the new firmware will only be active after a reboot.<br>
	<input type=submit name="action" value="Reboot" onClick="return confirm('The box will reboot now.\nYou will be connected again in 60 seconds.\n\nProceed?')">
	</form></body></html>
EOF
