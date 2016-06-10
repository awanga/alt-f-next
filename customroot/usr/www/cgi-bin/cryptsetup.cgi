#!/bin/sh

# $1-/dev/sd??
dstate() {
	if ! lsmod | grep -q '^dm_crypt'; then
		state="Not Loaded"
		action="Load"
		return
	fi

	state=$(dmsetup info $(basename $1)-crypt 2> /dev/null | awk '/State:/ {print $2}')
	if test "$state" = "ACTIVE"; then
		action="Close"
	else
		state="INACTIVE"
		action="Open"
	fi
}

. common.sh
check_cookie
write_header "Cryptsetup Setup"

mktt crypt_tt "Location of file with the encrypt password.<br>
Should be on removable USB medium, not on the<br>
same disk or box as the encrypted filesystem.<br>
Only needed when formating, opening or closing."

mktt cesa_tt "Using the hardware accelerator engine increases performance<br>
but can make some openSSL operations to fail (stunnel, e.g)"

CONFF=/etc/misc.conf

. $CONFF

if test "$MODLOAD_CESA" = "y"; then
	cesa_chk=checked
fi

rccryptsetup load >& /dev/null

devs="$(awk '/sd[a-z][1-9]/{printf "<option value=%s>%s (%.1f GB)</option>\n", $4, $4, $3*1024/1e9}' /proc/partitions)"

cat<<EOF
	<form id="cryptf" action="/cgi-bin/cryptsetup_proc.cgi" method="post">
	<fieldset><legend>Encrypt</legend>
	<table><tr><th>Device</th><th>Cipher</th><th>Bits</th><th></td></tr>
	<tr><td><select name=devto><option value=none>Select a Partition</option>$devs</select></td>
		<td><input type=text name=cipher value="aes-cbc-essiv:sha256"></td>
		<td><select name=nbits><option>128</option><option>192</option><option>256</option></select></td>
		<td><input type="submit" name=action value="Format" onClick="return confirm('All data in partition will be lost.\n\nProceed?')"></td></tr>
	</table></fieldset>
EOF

curr=$(blkid -t TYPE=crypt_LUKS | awk -F: '{print $1}')
action="none"

if test -n "$curr"; then
	cat<<-EOF
		<fieldset><legend>Encrypted devices</legend>
		<table><tr><th>Dev</th><th>Size (GB)</th><th>Cipher</th>
		<th>Mode</th><th>Bits</th><th>Hash</th><th>State</th></tr>
	EOF
	for i in $curr; do
		if ! cryptsetup isLuks $i >& /dev/null; then continue; fi
		dstate $i
		dsk=$(basename $i)
		eval $(cryptsetup luksDump $i | awk '\
			/Cipher name/ {printf "cipher=%s;", $3} \
			/Cipher mode/ {printf "mode=%s;", $3} \
			/Hash spec/ {printf "hash=%s;", $3} \
			/MK bits/ {printf "bits=%d;", $3}')
		cat<<-EOF
		<tr><td align=center>$dsk</td>
		<td align=right>$(cat /proc/partitions | awk '/'$dsk'/{printf "%.1f", $3 * 1024/1e9}')</td>
		<td align=center>$cipher</td>
		<td align=center>$mode</td>
		<td>$bits</td>
		<td align=center>$hash</td>
		<td>$state</td>
		<td><input type=submit name=$dsk value="$action"></td>
		</tr>
		EOF
	done

	echo "</table></fieldset>"
fi

cat<<-EOF
	<table>
	<tr><td>Use hardware accelerator</td><td><input type=checkbox $cesa_chk name=use_cesa value="yes" $(ttip cesa_tt)></td></tr>
	<tr><td>Password file:</td><td><input type=text name="keyfile" value="$CRYPT_KEYFILE" $(ttip crypt_tt)></td></tr>
	</table>
	<p><input type="submit" name=action value="Submit">$(back_button)
	</form></body></html>
EOF

