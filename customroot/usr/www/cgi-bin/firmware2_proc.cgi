#!/bin/sh

. common.sh
check_cookie
read_args

kernel_file=/tmp/kernel
initramfs_file=/tmp/initramfs
sqimage_file=/tmp/sqimage
defaults_file=/tmp/defaults

if test "$flash" = "Abort"; then
	rm -f $kernel_file $initramfs_file $sqimage_file $defaults_file > /dev/null 2>&1
	gotopage /cgi-bin/firmware.cgi
fi

# $1-file, $2-device, $3-msg
flash() {
	type=$(cat /sys/class/mtd/mtd0/type)
	if test "$type" = "nand"; then
		nand_flash $*
	elif test "$type" = "nor"; then
		nor_flash $*
	else
		msg "bummer!"
	fi
}

flash_error() {
	rm -f $TF $kernel_file $initramfs_file $sqimage_file $defaults_file
	echo "none" > /tmp/sys/power_led/trigger
	echo "Failed</p><br><p>You can repeat the fw download and firmware upgrade using HTTP<br>
	after stopping all running processes (System->Utilities->Services, StopAll)<br>or \"TryIt\" another firmware, but<br><strong><span class=\"error\">don't reboot or poweroff the box until success</span></strong><br> or you will need to buy and solder a serial cable into the box to make it work again.<br></p><pre>$1</pre></body></html>"
	rcsysctrl start
	exit 1
}

# rev-A:
# - Flashing kernel, it should take about 21 seconds: 23 Verifying... OK
# - Flashing rootfs, it should take about 86 seconds: 91 Verifying... OK
# 
# rev-B:
# - Flashing kernel, it should take about 21 seconds: 30 Verifying... OK
# - Flashing rootfs, it should take about 86 seconds: 109 Verifying... OK
# 
# rev-C:
# - Flashing kernel, it should take about 21 seconds: 47 Verifying... OK
# - Flashing rootfs, it should take about 86 seconds: 195 Verifying... OK 

nor_flash() {
	sz=$(stat -t $1 | cut -d" " -f2)
	tm=$(expr $sz / 75126 + 1); tm2=$(expr $tm \* 25 / 10)
	wait_count_start "<p>Flashing $3, it should take between $tm and $tm2 seconds"
	cat $1 > /dev/mtdblock${2:3} # use block device, no need to erase (no mtd-utils) 
	wait_count_stop

	echo "Verifying... "
	sync
	TF=$(mktemp)
	dd if=/dev/$2 of=$TF bs=$sz count=1 >& /dev/null
	if ! cmp $1 $TF >& /dev/null; then flash_error; fi
	echo "OK</p>"
	rm -f $TF
}

nand_flash() {
	echo "<p>$3: Erasing...&nbsp;"
	if ! res=$(flash_erase -q /dev/$2 0 0 2>&1); then flash_error "flash_erase: $res"; fi
	echo "flashing...&nbsp;"
	if ! res=$(nandwrite -qp /dev/$2 $1 2>&1); then flash_error "nandwrite: $res"; fi
	echo "verifying...&nbsp;"
	TF=$(mktemp)
	sz=$(stat -t $1 | cut -d" " -f2)
	if ! res=$(nanddump -ql $sz -f $TF /dev/$2 2>&1); then flash_error "nanddump: $res"; fi
	if ! dd if=$TF bs=$sz count=1 2> /dev/null | cmp $1 >& /dev/null; then flash_error "cmp:"; fi
	echo "OK</p>"
	rm -f $TF
}

check_fwfiles() {
	if ! test -f $kernel_file -a -f $initramfs_file; then
		rm -f $kernel_file $initramfs_file $sqimage_file $defaults_file
		cat<<-EOF
			<br>
			<form action="/cgi-bin/firmware.cgi" method="post">
			Kernel and/or ramdisk file missing <input type="submit" value="Retry">
			</form></body></html>
		EOF
		exit 0
	fi

	if test "$flash_defaults" = "flash" -a ! -s $defaults_file; then
		rm -f $kernel_file $initramfs_file $sqimage_file $defaults_file
		cat<<-EOF
			<br>
			<form action="/cgi-bin/firmware.cgi" method="post">
			defaults file missing or empty <input type="submit" value="Retry">
			</form></body></html>
		EOF
		exit 0
	fi
}

html_header "Firmware Updater"

if test "$flash" = "SpecialReboot"; then
	rm -f $initramfs_file $kernel_file $sqimage_file $defaults_file
	dd if=/dev/mtdblock2 of=/boot/zImage bs=64 skip=1 >& /dev/null
	dd if=/dev/mtdblock3 of=/boot/rootfs.arm.sqmtd bs=64 skip=1 >& /dev/null

elif test "$flash" = "TryIt"; then
	check_fwfiles
	dd if=$kernel_file of=/boot/zImage bs=64 skip=1 >& /dev/null
	dd if=$initramfs_file of=/boot/rootfs.arm.sqmtd bs=64 skip=1 >& /dev/null
	rm -f $initramfs_file $kernel_file $sqimage_file $defaults_file

elif test "$flash" = "FlashIt"; then
	check_fwfiles
	echo "<h3 class=\"error\">Don't poweroff or reboot the box until instructed to do it!<br>The upgrade takes at most five minutes to complete, and progress messages should be displayed.</h3><h4 class=\"warn\">If you suspect that something went wrong, you can try to repeat the firmware file download and upgrade using HTTP<br>
	after stopping all running processes (System->Utilities->Services, StopAll).<br></h4>"

	rcall stop >& /dev/null

	echo timer > /tmp/sys/power_led/trigger
	echo 50 > /tmp/sys/power_led/delay_off 
	echo 50 > /tmp/sys/power_led/delay_on

	if grep -qE 'DNS-321-Ax|DNS-323' /tmp/board; then
		kernel_mtd=mtd2
		initramfs_mtd=mtd3
		defaults_mtd=mtdblock0
		sqimage_mtd=""
	elif grep -qE 'DNS-327L|DNS-320-[AB]x|DNS-320L-Ax|DNS-325-Ax' /tmp/board; then
		kernel_mtd=mtd1
		initramfs_mtd=mtd2
		sqimage_mtd=mtd3
		if grep -qE 'DNS-327L' /tmp/board; then
			fs_type="-t ubifs"
			defaults_mtd=ubi0_0
		else
			fs_type="-t jffs2"
			defaults_mtd=mtdblock5
		fi
	else
		rcsysctrl start
		msg "bummer!"
	fi

	flash $kernel_file $kernel_mtd kernel
	flash $initramfs_file $initramfs_mtd rootfs

	if test -s $sqimage_file; then
		flash $sqimage_file $sqimage_mtd sqimage
	fi

	case "$flash_defaults" in
		"none")
			;;

		"clear")
			echo "<p>Erasing flashed settings, it should take some 5 seconds..."
			loadsave_settings -cf >& /dev/null
			;;

		"flashfile")
			echo "<p>Flashing new settings, it should take some 5 seconds..."
			TD=$(mktemp -d)
			mount $fs_type /dev/$defaults_mtd $TD
			rm -f $TD/*
			tar -C /tmp -xzf $defaults_file
			cp -f /tmp/default/* $TD
			umount $TD
			rm -rf $TD /tmp/default
			;;

		"recover")
			echo "<p>Recovering vendors settings from backup, it should take some 5 seconds..."
			loadsave_settings -rc  >& /dev/null
			;;
	esac

	# remove applied fixes and other customizations under /Alt-F,
	# avoiding that changed files with the same name in the new firmware will be shadowed
	fixup clean >& /dev/null

	rcsysctrl start >& /dev/null
	rm -f $kernel_file $initramfs_file $sqimage_file $defaults_file
	echo "none" > "/tmp/sys/power_led/trigger"
fi

cat<<-EOF
	<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
	You should reboot the box now for the new firmware to become active.
	<input type=submit name="action" value="Reboot" onClick="return confirm('The box will reboot now.\nYou will be connected again in 60 seconds.\n\nProceed?')">
	</form></body></html>
EOF
