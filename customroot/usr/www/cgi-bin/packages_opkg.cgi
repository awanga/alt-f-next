#!/bin/sh
. common.sh

check_cookie
write_header "Entware Package Manager"
parse_qstring

#debug

has_disks

echo "<h4 class="warn">Warning: Entware is alien to Alt-F, conflicts might arise.<br>Packages configuration files have to be manually edited.</h4>"

# FIXME: /opt should be really /mnt/<dev>/opt, and linked to /opt at discover time.
# It should not be a subdir of /Alt-F. Affected Alt-F packages: grep -l '/opt' ipkgfiles/*.p*
if ! aufs.sh -s >& /dev/null; then
	echo "<h3 class="warn">You have to install one Alt-F package first.</h3></body></html>"
	exit 0
fi

PATH=$PATH:/opt/bin:/opt/sbin
CONFF=/opt/etc/opkg.conf
OPTB=/opt/bin/opkg

if ! test -f $CONFF -a -x $OPTB; then
	arch=armv5sf-k3.2
	if  grep -q DNS-327L /tmp/board; then arch=armv7sf-k3.2; fi
	feed_1="http://bin.entware.net/$arch"
	cnt=1
	cat<<-EOF
		<form name="form" action="/cgi-bin/packages_opkg_proc.cgi" method=post>
		<input type=hidden name=nfeeds value="$cnt">
		<fieldset><legend>No Entware installation found</legend><table>
		<tr><td>Install from:</td><td><input type=text size=40 name=feed_1 value="$feed_1"></td></tr>
		<tr><td>install into:</td>
		<!--td>$(select_part)</td--><td>$(realpath /Alt-F)/opt</td></tr>
		<tr><td></td><td><input type=submit name=install value=Install></td></tr></table></fieldset>
		</form></body></html>
	EOF
	exit 0
fi

cat<<-EOF
	<script type="text/javascript">
	function ask() {
		return confirm("All packages and its configurations files will be deleted.\\nYou will have to reinstall all Entware packages.");
	}
	</script>
	<form name="form" action="/cgi-bin/packages_opkg_proc.cgi" method=post>
	<fieldset><legend>Package Feeds</legend><table>
	<tr><th>Disabled</th><th>Feed</th></tr>
EOF

cnt=1
while read type name feed; do
	cmt=""
	if test \( "$type" = "src/gz" -o "$type" = "#!#src/gz" \) -a -n "$feed"; then
		if test "$type" = "#!#src/gz"; then
			cmt=checked
		fi
		echo "<tr><td align=\"center\"><input type=checkbox $cmt name=dis_$cnt></td><td><input type=text size=40 name=feed_$cnt value=\"$feed\"></td></tr>"
		cnt=$((cnt+1))
	fi
done < $CONFF

cat<<-EOF
	<tr><td align="center"><input type=checkbox name=dis_$cnt></td><td><input type=text size=40 name=feed_$cnt value=""></td></tr>
	<tr><td></td><td><input type=submit name=changeFeeds value=Submit>
	<input type=submit name=updatelist value=UpdatePackageList></td></tr>
	</table>
	<input type=hidden name=nfeeds value="$cnt">
	</fieldset>
	<fieldset><legend>Search package</legend><table>
	<tr><td>search string:</td><td><input type=text size=40 name=search value="$search" onkeypress="return event.keyCode != 13"></td>
	<td><input type=submit name=asearch value=Search></td></tr>
EOF

if test -n "$search"; then
	a=$(opkg find '*'$search'*' ) # avoid recursive opkg calls
	echo "$a" | awk -F' - ' '{
		op="Remove"
		cmd=sprintf("opkg status %s | grep -q installed", $1)
		if (system(cmd))
			op="Install"
		printf("<tr><td>%s</td><td>%s</td> \
		<td><input type=submit name=\"%s\" value=\"%s\"></td> \
		<td>%s</td></tr>", $1, $2, $1, op, $3)
		nfound++
	}
	END{
		if (nfound == 0)
		printf("<tr><td colspan=3>No \"'$search'\" string found in any package name or description</td></tr>")
	}'
fi

echo "</table></fieldset>"
opkg -V0 info | awk -v printall=$search '
	/Package:/ { i++; nm=$2; pkg[i] = nm } # this relies on Package being the first field 
	/Version:/ { ver[i] = $2 }
	/Description:/ { des[i] = substr($0, index($0,$2)) }
	/Status:/ { if ($4 == "installed") inst[nm] = i; else { uinst[nm] = i; ucnt++; } }
	END {
		print "<fieldset><legend> Installed Packages </legend> \
			<table><tr> \
				<th>Name</th><th>Version</th><th></th><th></th><th></th><th>Description</th> \
			</tr>"

		update = 0;
		for (i=1; pkg[i] != ""; i++) {
			nm = pkg[i];
			if (nm in inst) {
				rmv = sprintf("<td><input type=submit name=\"%s\" value=Remove></td>", nm);

				if (nm in uinst) {	# new version available, old has missing info
					j = uinst[nm]; update++;

					v = ver[inst[nm]];

					if (system("opkg -V0 compare_versions " v " \">\" " ver[uinst[nm]]))
						upd="<td></td><td></td>";
					else
						upd = sprintf("<td><input type=submit name=\"%s\" value=Update></td><td>(%s)</td>", nm, ver[uinst[nm]]);

					delete uinst[nm]; ucnt--; delete inst[nm]; 
				} else {
					j = i; v = ver[i];
					upd="<td></td><td></td>";
				}

				printf "<tr><td>%s</td><td>%s</td>", nm, v;
				print rmv;
				print upd;
				printf "<td>%s</td></tr>\n\n", des[j];
			}
		}

		print "<tr><td colspan=6><br></td></tr>"
		if (update != 0)
			print "<tr><td colspan=2><strong>Update all installed</strong></td> \
				<td><input type=submit name=updateall value=UpdateAll></td></tr>"
		print "<tr><td colspan=2><strong>Remove all installed</strong></td> \
				<td colspan=4><input type=submit name=removeall value=RemoveAll onclick=\"return ask()\"></td></tr>"
		print "</table></fieldset>"

		if (length(printall) == 0) {
			print "<fieldset><legend> Available Packages </legend><table>"

			if (ucnt == 0) {
				print "None"
			} else {
				print "<tr><th>Name</th><th>Version</th> \
					<th></th><th>Description</th></tr>"

				for (i=1; pkg[i] != ""; i++) {
					nm = pkg[i];
					if (nm in uinst) {
						printf "<tr><td>%s</td><td>%.12s</td>",nm, ver[i];
						printf "<td><input type=submit name=\"%s\" value=Install></td>", nm;
						printf "<td>%s</td></tr>\n\n", des[i];
					}
				}
			}
			print "</table></fieldset>"
		}
		print "</form></body></html>"
	}'
