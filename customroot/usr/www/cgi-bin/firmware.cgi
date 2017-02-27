#!/bin/sh

. common.sh
check_cookie
write_header "Firmware Updater"

brd=$(cat /tmp/board)
if test "$brd" = "Unknown"; then
	echo "<h3 class=\"error\">Unsupported unknown board</h3></body></html>"
	exit 1
fi

# FIXME: relies on NOR /dev/mtd2 (kernel for DNS-321|DNS-323, initramfs for DNS-320|DNS-320L|DNS-325)
	if grep -qE 'DNS-321-Ax|DNS-323' /tmp/board; then
		kernel=mtd2
		initramfs=mtd3
	elif grep -qE 'DNS-327L|DNS-320-[AB]x|DNS-320L-Ax|DNS-325-Ax' /tmp/board; then
		kernel=mtd1
		initramfs=mtd2
	else
		echo "<h3 class=\"error\">BUMMER, unknown board</h3></body></html>"
		exit 1
	fi

flashed_kernel=$(dd if=/dev/$kernel ibs=32 skip=1 count=1 2> /dev/null | grep -o 'Alt-F.*')
flashed_initramfs=$(dd if=/dev/$initramfs ibs=32 skip=1 count=1 2> /dev/null | grep -o 'Alt-F.*')
if ! echo $flashed_kernel $flashed_initramfs | grep -q Alt-F; then
	fw="the vendor's firmware"
fi

if losetup | grep -q /dev/mtdblock3; then
	cat<<-EOF
		<h4 class="warn">To flash Alt-F you have to reboot into a special mode by hitting
		the "SpecialReboot" button,<br> and afterwards the "Reboot" button.
		After rebooting run again the "Firmware Updater".<br><br>
		If however you only want to try a new Alt-F fw you can proceed with the upload section bellow.</h4>
		<form action="/cgi-bin/firmware2_proc.cgi" method="post">
		<center><input type=submit name=flash value="SpecialReboot"></center>
		</form>
	EOF
fi

cat<<-EOF
	<h3 class="error">By following this procedure you can
	<a href="http://en.wikipedia.org/wiki/Brick_%28electronics%29">brick</a>
	 your box.<br></h3>

	However, it was used to successfully flash D-Link and Alt-F firmware on a <strong>DNS-323 Rev-A1/B1</strong>, a <strong>DNS-325 rev-A1</strong>, a <strong>DNS-320L rev-A1</strong> and on a <strong>DNS-327L rev-A1</strong> boxes.
	Other compatible boards are said to work.<br><br>

	An option is offered latter to cancel the procedure, so you can safely proceed for now.

	<p>The box is currently running Alt-F $(cat /etc/Alt-F) with kernel $(uname -r), and flashed with "$flashed_initramfs" and kernel "$flashed_kernel".</p>
EOF

cat<<-EOF
	<form action="/cgi-bin/firmware_proc.cgi" method="post" enctype="multipart/form-data">
	<table>
	<tr><td>Firmware binary .bin file to upload:</td><td><input type=file name=fw.bin></td></tr>
	<tr><td>Firmware verification .sha1 file to upload:</td><td><input type=file name=fw.sha1> (optional)</td></tr>
	<tr><td></td><td><input type=submit value="Upload"></td></tr>
	</table>
	</form>
	</body></html>
EOF
