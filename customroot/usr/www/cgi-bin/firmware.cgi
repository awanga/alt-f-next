#!/bin/sh

. common.sh
check_cookie
write_header "Firmware Update"
cat<<-EOF
	<h3><font color=red>By following this procedure you can
	<a href="http://en.wikipedia.org/wiki/Brick_%28electronics%29">brick</a>
	 your box.<br></font></h3>

	However, it was used to successfully flash
	DLink 1.07, DLink 1.08, Conceptronic 1.05b5<br>
	and Alt-F-0.1Bx firmware on a <strong><u>Rev-B1 board</u></strong>.<br><br>

	An option is offered latter to cancel the procedure, so you can safely proceed for now.

	<p>The box is currently running Alt-F $(cat /etc/Alt-F).</p>

	<form action=/cgi-bin/firmware_proc.cgi method=post enctype=multipart/form-data>
	Firmware file to upload: 
	<input type=file name=file1><input type=submit value="Upload">
	</form>
	</body></html>
EOF
