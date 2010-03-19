#!/bin/sh

. common.sh
check_cookie

write_header "NTP Setup"

CONFF=/etc/ntp.conf

eval $(grep ^NTPD_DAEMON $CONFF)
eval $(grep ^NTPD_BOOT $CONFF)

sel_cron=""; sel_daemon=""; sel_boot=""

if test "$NTPD_DAEMON" = "yes"; then
	sel_daemon="CHECKED"
else
	sel_cron="CHECKED"
fi

if test "$NTPD_BOOT" = "yes"; then
	sel_boot="CHECKED"
fi

cat <<-EOF
	<script type="text/javascript">
	function toogle() {
		document.getElementById("bootcheck").disabled = document.getElementById("bootcheck").disabled ? false : true;
	 }
	</script>

	<form name=ntp action=ntp_proc.cgi method="post" >
	<input type=radio $sel_daemon name=runasdaemon value=yes>
		Run continuously as a daemon<br>
	<input type=radio $sel_cron name=runasdaemon value=no>
		Run everyday at 6:00<br><br>
	<input type=checkbox id=bootcheck $sel_boot name=runatboot value=yes>
		Adjust time at boot<br> 
	<br><table>
EOF

cnt=1
while read arg server; do
	if test "$arg" = "server" -a "$server" != "127.127.1.0"; then
		echo "<tr><td>Server $cnt</td>
			<td><input type=text size=20 name=server_$cnt value=$server></td></tr>"
		cnt=$(($cnt+1))
	fi
done < $CONFF

for i in $(seq $cnt 3); do
		echo "<tr><td>Server $i</td>
			<td><input type=text size=20 name=server_$i></td></tr>"
done

cat<<-EOF
	<tr><td></td><td><input type=submit value=Submit>
	<input type=button name=back value="Back" onclick="history.back()"></td></tr>
	</table></form></body></html>
EOF
