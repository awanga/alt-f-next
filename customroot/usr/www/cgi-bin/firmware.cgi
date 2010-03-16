#!/bin/sh

. common.sh
check_cookie
write_header "Firmware Setup"
cat<<-EOF
  <center>
  <h3><font color=red>
    By following this procedure you can brick your box.<br>
  </font></h3>
  <h4>However, it was used to successfully flash</h4>
  <h4>Dlink 1.07, Conceptronic 1.05b5 and Alt-F-0.1B1 firmware</h4>
  <h4> on a <u>Rev-B1 board</u>, and an option is offered latter to abort.</h4>	
  <p><center>Currently using Alt-F $(cat /etc/Alt-F)</center></p>
  <form action=/cgi-bin/firmware_proc.cgi method=post enctype=multipart/form-data>
  Firmware file to upload: 
  <input type=file name=file1><input type=submit value="Upload">
  </form></center>
  </body></html>
EOF
