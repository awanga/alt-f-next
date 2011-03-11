#!/bin/sh

. common.sh
check_cookie
write_header "Debian Setup"

mktt kexec_tt "When executed, Debian will replace Alt-F during its execution<br>
and you will have to ssh the box and use the command line.<br>
You can login using the 'root' username, without quotes, with the<br>
default passwd of '1234', without quotes.<br>
To return to Alt-F, execute the command 'alt-f'."

mktt rm_tt "Delete the Debian installation from disk."

mktt install_tt "Debian will be installed in the root of the selected filesystem, not in a directory.<br>
It is recommended, although not necessary, to dedicate the selected filesystem to Debian.<br>
A minimum installation will need at least 200MB. Additional packages will need more space."

# check installed:

inst=$(find /mnt -maxdepth 3 -name initrd.img-\*-orion5x)

for i in $inst; do
	dn=$(dirname $i)
	dbpart=$(dirname $dn)
	if test -f ${dn}/vmlinuz-*-orion5x -a -f ${dbpart}/etc/apt/sources.list; then
		mirror=$(cut -d" " -f2 ${dbpart}/etc/apt/sources.list)
		break;
	fi
done

cat<<-EOF
	<form name="debianf" action="/cgi-bin/debian_proc.cgi" method="post">
	<script type="text/javascript">
		function up_mirror() {
			document.debianf.mirror.value = document.debianf.sel_mirror.value;
		}
	</script>
EOF

if test -n "$mirror" -a -n "$dbpart"; then
	cat<<-EOF
		<fieldset><legend><strong>Found a $(cat $dbpart/etc/issue.net) installation in $dbpart</strong></legend>
		<input type="submit" name="submit" value="Execute" $(ttip kexec_tt) onClick="return confirm('Executing Debian will stop Alt-F and all its services.\n\n\
You will have to use a ssh client to login as user root,\n\
default password 1234 and use the command line.\n\nProceed?')">
		<input type="submit" name="submit" value="Uninstall" $(ttip rm_tt)></fieldset><br>
	EOF
fi

cat<<-EOF
	<fieldset><legend><strong>Install Debian</strong></legend>
	<table>
	<tr><td>Debian mirror:</td>
	<td><input type=text size=30 name=mirror value=$mirror></td>
	<td><select name=sel_mirror onChange="up_mirror()">
	<option value="none">Select one</option>
EOF

while read url country; do
	sel=""; if test "$url" = "$mirror"; then sel="selected"; fi
	echo "<option $sel value=\"$url\">$(echo $country | tr '_' ' ')</option>"
done < deb-mirrors.txt

cat<<-EOF
	</select></td></tr>
	<tr><td>Install in</td>
	<td>$(select_part $(basename $dbpart))</td>
	<td><input type="submit" name="submit" value="Install" $(ttip install_tt)></td>
	</tr></table></fieldset>
	</form></body></html>
EOF

