#!/bin/sh

. common.sh
check_cookie
write_header "Firmware Update"
cat<<-EOF
	<center>
	<h3><font color=red>By following this procedure you can
	<a href="http://en.wikipedia.org/wiki/Brick_%28electronics%29">brick</a>
	 your box.<br></font></h3>
	<h4>However, it was used to successfully flash<br>
	DLink 1.07, DLink 1.08, Conceptronic 1.05b5 and Alt-F-0.1B1<br>
	firmware on a <u>Rev-B1 board</u>.<br><br>
	An option is offered latter to cancel the procedure.</h4>
	<h4>Before proceeding you should stop all running services</h4>
	<p><center>Currently using Alt-F $(cat /etc/Alt-F)</center></p>
	<form action=/cgi-bin/firmware_proc.cgi method=post enctype=multipart/form-data>
	Firmware file to upload: 
	<input type=file name=file1><input type=submit value="Upload">
	</form></center>
	</body></html>
EOF
