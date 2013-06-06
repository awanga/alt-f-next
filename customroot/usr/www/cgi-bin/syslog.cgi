#!/bin/sh

# Copyright (c) 2010 Augusto Bott <augusto at bott com br>
# Licence GNU GPL, see the /COPYING file for details

. common.sh
check_cookie

write_header "System and Kernel log daemon setup" "toggle_remote()"

CONFF=/etc/syslog.conf

log_remote="0"
log_internal="1"
log_remote_host=""
log_remote_port="514"
log_drop_dups="1"
log_smaller_output="0"

if test -e $CONFF; then
	. $CONFF
fi

if test "$log_internal" = "1"; then
	log_internal_checked="checked"
fi

if test "$log_remote" = "1"; then
	log_remote_checked="checked"
fi

if test "$log_drop_dups" = "1"; then
	log_drop_dups_checked="checked"
fi

if test "$log_smaller_output" = "1"; then
	log_smaller_output_checked="checked"
fi

cat <<-EOF
<script type="text/javascript">
function toggle_remote() {
	if (document.getElementById("log_remote").checked) {
		document.getElementById("log_remote_host").disabled=false;
		document.getElementById("log_remote_port").disabled=false;
		document.getElementById("log_internal").disabled=false;
	} else {
		document.getElementById("log_remote_host").disabled=true;
		document.getElementById("log_remote_port").disabled=true;
		document.getElementById("log_internal").disabled=true;
	}
}
</script>
<form name="syslog" action="/cgi-bin/syslog_proc.cgi" method="post">
<table>
	<tr>
		<td>Drop duplicate messages</td>
		<td><input type="checkbox" $log_drop_dups_checked name="log_drop_dups" value="1"></td>
	</tr>
	<tr>
		<td>Smaller logging output</td>
		<td><input type="checkbox" $log_smaller_output_checked name="log_smaller_output" value="1"></td>
	</tr>
	<tr>
		<td>Log to remote system</td>
		<td><input type="checkbox" $log_remote_checked name="log_remote" id="log_remote" value="1" onClick="toggle_remote()"></td>
	</tr>
	<tr>
		<td>Log also internally</td>
		<td><input type="checkbox" $log_internal_checked name="log_internal" id="log_internal" value="1"></td>
	</tr>
	<tr>
		<td>Remote system IP:port</td>
		<td><input type="text" size="20" name="log_remote_host" id="log_remote_host" value="$log_remote_host">:<input type="text" size="5" name="log_remote_port" id="log_remote_port" value="$log_remote_port"></td>
	</tr></table>
	<p><input type=submit value=Submit> $(back_button)
	</form></body></html>
EOF

