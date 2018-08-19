#!/bin/sh

. common.sh
check_cookie

write_header "NTP Setup"

CONFN=/etc/ntp.conf
CONFF=/etc/misc.conf

if test -e $CONFF; then
	. $CONFF
fi

sel_cron=""; sel_daemon=""; sel_boot=""
if test "$NTPD_DAEMON" = "yes"; then
	sel_daemon="checked"
else
	sel_cron="checked"
	croni=$NTPD_DAEMON
fi

if test "$NTPD_BOOT" = "yes"; then
	sel_boot="CHECKED"
fi

opt=""
for i in 24 12 6; do
	if test "$i" = "$croni"; then
		opt="$opt<option selected>$i</option>"
	else
		opt="$opt<option>$i</option>"
	fi
done

cat <<-EOF
	<script type="text/javascript">
	function toogle() {
		document.getElementById("bootcheck").disabled = document.getElementById("bootcheck").disabled ? false : true;
	 }
	</script>

	<form name=ntp action=ntp_proc.cgi method="post" >
	<input type=radio $sel_daemon name=runasdaemon value=yes>
		Run continuously as a server<br>
	<input type=radio $sel_cron name=runasdaemon value=no>
	Run once every <select name=croni>$opt</select> hours<br><br>
	<input type=checkbox id=bootcheck $sel_boot name=runatboot value=yes>
		Adjust time when starts<br> 
	<br><table>
EOF

cnt=1
while read arg server; do
	if test "$arg" = "server" -a "$server" != "127.127.1.0"; then
		echo "<tr><td>Server $cnt</td>
			<td><input type=text size=20 name="server_$cnt" value="$server"></td></tr>"
		cnt=$(($cnt+1))
	fi
done < $CONFN

for i in $(seq $cnt 3); do
		echo "<tr><td>Server $i</td>
			<td><input type=text size=20 name="server_$i"></td></tr>"
done

cat<<-EOF
	</table>
	<p><input type=submit value=Submit>$(back_button)
	</form></body></html>
EOF
