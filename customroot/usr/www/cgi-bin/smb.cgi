#!/bin/sh

. common.sh
check_cookie

# while the real page is not written, go directly to the swat web page
gotopage http://$(hostname -i | sed 's/ //'):901

write_header "Samba Setup"

cat<<-EOF
	<form action=smb_proc.cgi method="post">
	<fieldset>
	<legend><strong>Directories to export to other hosts</strong></legend>
	Write Me
	</fieldset>

	<fieldset>
	<legend><strong>Directories to import from other hosts</strong></legend>
	Write Me
	</fieldset>

	<input type=submit name=swat value="Advanced">$(back_button)
	</form></body></html>
EOF

