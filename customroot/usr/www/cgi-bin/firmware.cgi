#!/bin/sh

. common.sh
check_cookie
write_header "Firmware Update"

brd=$(cat /tmp/board)
if test "$brd" = "Unknown"; then
	echo "<h3 class=\"error\">Unsupported unknown board</h3></body></html>"
	exit 1
fi

# FIXME: relies on NOR /dev/mtd2 (kernel for DNS-321|DNS-323, initramfs for DNS-320|DNS-320L|DNS-325)
flashed_firmware=$(dd if=/dev/mtd2 ibs=32 skip=1 count=1 2> /dev/null | grep -o 'Alt-F.*')
if echo $flashed_firmware | grep -q Alt-F; then
	fw="$flashed_firmware"
else
	fw="the vendor's firmware"
fi

cat<<-EOF
	<h3 class="error">By following this procedure you can
	<a href="http://en.wikipedia.org/wiki/Brick_%28electronics%29">brick</a>
	 your box.<br></h3>

	However, it was used to successfully flash D-Link and Alt-F firmware on a <strong>DNS-323 Rev-B1</strong>, a <strong>DNS-325 rev-A1</strong> and on a <strong>DNS-320L rev-A1</strong> boxes.
	Other compatible boards are said to work.<br><br>

	An option is offered latter to cancel the procedure, so you can safely proceed for now.

	<p>The box is currently running Alt-F $(cat /etc/Alt-F) with kernel $(uname -r), and flashed with $fw.</p>

	<form action="/cgi-bin/firmware_proc.cgi" method="post" enctype="multipart/form-data">
	Firmware file to upload: 
	<input type=file name=file1><input type=submit value="Upload">
	</form>
	</body></html>
EOF
