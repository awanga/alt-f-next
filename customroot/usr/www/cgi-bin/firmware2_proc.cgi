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

html_header
echo "<center><h2>Firmware Updater</h2></center>"

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
	# is it a initrd or a initramfs?
	#TF=$(mktemp -d)
	#mount -o loop /root/rootfs.arm.sqmtd $TF >& /dev/null
	#st=$?
	#umount $TF >& /dev/null
	#if test $st != 0; then # mount fails, it is a initramfs
	#	echo "console=ttyS0,115200" > /root/cmdline
	#	# or mv /root/rootfs.arm.sqmtd /root/rootfs.arm.cpio.lzma
	#fi

elif test "$flash" = "FlashIt"; then
	rcall stop >& /dev/null

	echo timer > "/sys/class/leds/power:blue/trigger"
	echo 50 > "/sys/class/leds/power:blue/delay_off" 
	echo 50 > "/sys/class/leds/power:blue/delay_on"

	wait_count_start "<p>Flashing the kernel, it takes about 25 seconds"
	cat $kernel_file > /dev/mtdblock2 
	sleep 3
	wait_count_stop

	wait_count_start "<p>Flashing the ramdisk, it takes about 110 seconds"
	cat $initramfs_file > /dev/mtdblock3 
	sleep 3
	wait_count_stop

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
	The new firmware will only be active after a reboot.
	<input type=submit name="action" value="Reboot" onClick="return confirm('The box will reboot now.\nYou will be connected again in 60 seconds.\n\nProceed?')">
	</form></body></html>
EOF

