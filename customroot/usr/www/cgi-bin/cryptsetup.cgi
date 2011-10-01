#!/bin/sh

. common.sh
check_cookie
write_header "Cryptsetup Setup"

CONFF=/etc/misc.conf

if test -f $CONFF; then
	. $CONFF
fi

mktt crypt_tt "Location of file with the encrypt password.<br>
Should be on removable medium, not on the<br>
same disk or box as the encrypted filesystem."

curr=$(blkid -t TYPE=crypt_LUKS | awk -F: '{print $1}')

echo '<form id="cryptf" action="/cgi-bin/cryptsetup_proc.cgi" method="post">'

if test -n "$curr"; then
	cat<<-EOF
	<fieldset><legend><strong>Encrypted devices</strong></legend>
	<table><tr><th>Dev</th><th>Size (GB)</th></tr>
	EOF
	for i in $curr; do
		dsk=$(basename $i)
		cat<<-EOF
		<tr><td>$dsk</td>
		<td>$(cat /proc/partitions  | awk '/'$dsk'/{printf "%.1f", $3 * 1024/1e9}')</td>
		<td></td>
		</tr>
		EOF
	done
	echo "</table></fieldset><br>"
fi

devs="$(awk '/sd[a-z][1-9]/{printf "<option value=%s>%s (%.1f GB)</option>\n", $4, $4, $3*1024/1e9}' /proc/partitions)"

cat<<EOF
	<fieldset><legend><strong>Device to Format and Encrypt</strong></legend>
	<select name=devto>
	<option value=none>Select a Partition</option>$devs</select>
	<input type="submit" name=action value="Format" onClick="return confirm('All data in partition will be lost.\nNo check will be done to see if the partition is currently in use.\n\nProceed?')">
	</fieldset><br>

	<table>
	<tr><td>Password file:</td><td><input type=text name="keyfile" value="$CRYPT_KEYFILE" $(ttip crypt_tt)></td></tr>
	<tr><td></td><td><input type="submit" name=action value="Submit">$(back_button)</td></tr>
	</table></form></body></html>
EOF


