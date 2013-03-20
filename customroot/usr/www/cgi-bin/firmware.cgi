#!/bin/sh

. common.sh
check_cookie
write_header "Firmware Update"

brd=$(cat /tmp/board)
if test "$brd" = "Unknown"; then
	echo "<center><h3><font color=red>Unsupported unknown board</font></h3></center></body></html>"
	exit 1
fi

cat<<-EOF
	<center><h3><font color=red>By following this procedure you can
	<a href="http://en.wikipedia.org/wiki/Brick_%28electronics%29">brick</a>
	 your box.<br></font></h3></center>

	However, it was used to successfully flash
	DLink 1.07, 1.08, 1.09, 1.10 and Conceptronic 1.05b5<br>
	and all Alt-F firmware versions on a <strong><u>Rev-B1 board</u></strong>.<br><br>

	An option is offered latter to cancel the procedure, so you can safely proceed for now.

	<p>The box is currently running Alt-F $(cat /etc/Alt-F).</p>

	<form action="/cgi-bin/firmware_proc.cgi" method="post" enctype="multipart/form-data">
	Firmware file to upload: 
	<input type=file name=file1><input type=submit value="Upload">
	</form>
	</body></html>
EOF
