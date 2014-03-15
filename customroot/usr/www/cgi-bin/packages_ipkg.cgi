#!/bin/sh
. common.sh

check_cookie
write_header "Alt-F Package Manager"

#debug

if ! ipkg status >/dev/null; then
	has_disks
	
	CONFF=/etc/ipkg.conf
	cat<<-EOF
		<form action="/cgi-bin/packages_ipkg_proc.cgi" method=post>
		<fieldset><legend>Package Feeds</legend><table>
		<tr><th>Disabled</th><th>Feed</th></tr>
	EOF

	cnt=1
	while read type name feed; do
		cmt=""
		if test \( "$type" = "src" -o "$type" = "#!#src" \) -a -n "$feed"; then
			if test "$type" = "#!#src"; then
				cmt=checked
			fi
			echo "<tr><td align=\"center\"><input type=checkbox $cmt name=dis_$cnt></td><td><input type=text size=40 name=feed_$cnt value=\"$feed\"></td></tr>"
			cnt=$((cnt+1))
		fi
	done < $CONFF

	cat<<-EOF
		<tr><td align="center"><input type=checkbox name=dis_$cnt></td><td><input type=text size=40 name=feed_$cnt value=""></td></tr>
		</table>
		<input type=hidden name=nfeeds value="$cnt">
		</fieldset>
		<h4>No ipkg instalation found, install ipkg in:</h4>
	EOF

	select_part
	echo "</select><input type=submit name=install value=Install>
	</form></body></html>"

else
	ipkg-cl -V0 info | awk '
	BEGIN {
		print "<script type=\"text/javascript\"> \
				function ask() { \
					return confirm(\"All packages files and configurations will be deleted.\\nYou will have to reinstall all Alt-F packages.\"); \
				} \
			</script> \
			<form action=\"/cgi-bin/packages_ipkg_proc.cgi\" method=\"post\"> \
			<fieldset><legend>Configure Feeds</legend> \
			<table><tr><th>Disabled</th><th>Feed</th></tr>";
		nf=1;
		while (getline ln <"/etc/ipkg.conf") {
			split(ln,a);
			if (a[1] == "src")
				a[1]="";
			else if (a[1] == "#!#src")
				a[1]="checked";
			else
				continue;
			printf "<tr><td align=\"center\"><input type=checkbox %s name=dis_%d></td>", a[1], nf;
			printf "<td><input type=text size=50 name=feed_%d value=\"%s\"></td></tr>\n", nf, a[3];
			nf++
		}
		printf "<tr><td align=\"center\"><input type=checkbox name=dis_%d></td> \
			<td><input type=text size=50 name=feed_%d value=\"\"></td></tr> \
			<input type=hidden name=nfeeds value=\"%d\">", nf, nf, ++nf;
		if (system("test -f /etc/preinst") == 0)
			while (getline ln <"/etc/preinst") {
				split(ln,a);
				preinst[a[1]] = a[2];
			}
	}
	/Package:/ { i++; nm=$2; pkg[i] = nm } # this relies on Package being the first field 
	/Version:/ { ver[i] = $2 }
	/Source:/ { url[i] = $2 }
	/Description:/ { des[i] = substr($0, index($0,$2)) }
	/Status:/ { if ($4 == "installed") inst[nm] = i; else { uinst[nm] = i; ucnt++; } }
	END {
		print "<tr><td></td><td><input type=submit name=Submit value=Submit> \
			<input type=submit name=updatelist value=UpdatePackageList> \
			</table></fieldset> \
			<fieldset><legend> Installed/Pre-installed Packages </legend> \
			<table><tr> \
				<th>Name</th><th>Version</th><th></th><th></th><th></th><th>Description</th> \
			</tr>"

		update = 0;
		for (i=1; pkg[i] != ""; i++) {
			nm = pkg[i];
			if (nm in inst || nm in preinst) {

				remdis = ""
				if (nm in preinst && ! (nm in inst)) { # pre-instaled uninstalled
					remdis = "disabled"
				} else if (nm in preinst && nm in inst) { # pre-instaled updated
					if (preinst[nm] == ver[inst[nm]])
						remdis = "disabled"
				}
				rmv = sprintf("<td><input type=submit %s name=%s value=Remove></td>", remdis, nm);

				if (nm in uinst) {	# new version available, old has missing info
					j = uinst[nm]; update++;

					if (nm in preinst && ! (nm in inst))
						v = preinst[nm]
					else
						v = ver[inst[nm]];

					if (v == ver[uinst[nm]])
						upd="<td></td><td></td>";
					else
						upd = sprintf("<td><input type=submit name=%s value=Update></td><td>(%s)</td>", nm, ver[uinst[nm]]);

					delete uinst[nm]; ucnt--; delete inst[nm]; delete preinst[nm]
				} else {
					j = i; v = ver[i];
					upd="<td></td><td></td>";
				}

				printf "<tr><td><a href=\"/cgi-bin/embed.cgi?name=%s?site=%s\">%s</a></td><td>%s</td>",
					nm, url[j], nm, v;
				print rmv;
				print upd;
				printf "<td>%s</td></tr>\n\n", des[j];
			}
		}
	
		print "<tr><td colspan=6><br></td></tr>"
		if (update != 0)
			print "<tr><td colspan=2><strong>UpdateAll</strong></td> \
				<td><input type=submit name=updateall value=UpdateAll></td></tr>"

		print "<tr><td colspan=2><strong>Remove all installed</strong></td> \
				<td colspan=4><input type=submit name=removeall value=RemoveAll onclick=\"return ask()\"></td></tr> \
			</table></fieldset> \
			<fieldset><legend> Available Packages </legend><table>"

		if (ucnt == 0) {
			print "None"
		} else {
			print "<tr><th>Name</th><th>Version</th> \
				<th></th><th>Description</th></tr>"

			for (i=1; pkg[i] != ""; i++) {
				nm = pkg[i];
				if (nm in uinst) {
					printf "<tr><td><a href=\"/cgi-bin/embed.cgi?name=%s?site=%s\">%s</a></td><td>%s</td>",
					nm, url[i], nm, ver[i];
					printf "<td><input type=submit name=%s value=Install></td>", nm;
					printf "<td>%s</td></tr>\n\n", des[i];
				}
			}
		printf ("<tr><td colspan=4><br></td></tr><tr><td colspan=2><strong>Install all available</strong></td> \
			<td colspan=2><input type=submit name=installall value=InstallAll></td></tr>\
		</table></fieldset></form>", pkgfeed)
		}
	}'
fi
