#!/bin/sh

. common.sh
check_cookie
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

	<input type=submit name=swat value="Advanced">
	<input type=button name=back value="Back" onclick="history.back()">
	</form></body></html>
EOF

