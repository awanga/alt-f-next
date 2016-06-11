#!/bin/sh
. common.sh

check_cookie
write_header "Alt-F Package Manager"

#debug

has_disks

CONFF=/etc/ipkg.conf
cat<<-EOF
	<form name="form" action="/cgi-bin/packages_ipkg_proc.cgi" method=post>
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
	<tr><td></td><td><input type=submit name=changeFeeds value=Submit>
	<input type=submit name=updatelist value=UpdatePackageList>
	</table>
	<input type=hidden name=nfeeds value="$cnt">
	</fieldset>
	<fieldset><legend>Packages Installed On</legend>
EOF

install_loc=$(find /mnt -type d -maxdepth 2 -name Alt-F)
if test -z "$install_loc"; then
	cat<<-EOF
		<table><tr><td>No Alt-F package instalation found, install in:</td>
		<td>$(select_part)</td>
		<td><input type=submit name=install value=Install></td></table>
	EOF
else
	echo "<table><tr><th>FS</th><th class="highcol">Boot Enabled</th><th>Status</th></tr>"
	j=0
	for i in $install_loc; do
		j=$((++j))
		chk=""
		if ! test -f "$i"/NOAUFS; then
			chk=checked
		fi
		act="ActivateNow"; st="Inactive"
		if test "$(realpath /Alt-F 2> /dev/null)" = "$i"; then
			act="DeactivateNow"; st="<strong>Active</strong>"
		fi

		cat<<-EOF
			<tr><td>$(basename $(dirname $i))</td>
			<td class="highcol" align="center"><input type=checkbox $chk name="$i" value="BootEnable_$j"></td>
			<td>$st</td>
			<td><input style="width:100%" type=submit name="$i" value=$act></td>
			<td><input type=submit name="$i" value=Delete onClick="return confirm('Delete $i and all its files and subfolders?\nAll packages files and configurations will be deleted.\nYou will have to reinstall all Alt-F packages.')"></td>
			<td><input type=hidden name=altf_dir_$j value="$i">
			<input type=submit name="$j" value=CopyTo>$(select_part "" $j)</td>
			</tr>
		EOF
	done
	cat<<-EOF
		<tr><td></td><td class="highcol"><input type=submit name="BootEnable" value="Submit"></td></tr>
		</table>
		<input type=hidden name=ninstall value="$j"">
	EOF
fi
echo "</fieldset>"

if ipkg status >/dev/null; then
	ipkg-cl -V0 info | awk '
	BEGIN {
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
		print "<fieldset><legend> Installed/Pre-installed Packages </legend> \
			<table><tr> \
				<th>Name</th><th>Version</th><th></th><th></th><th></th><th>Description</th> \
			</tr>"

		update = 0;
		for (i=1; pkg[i] != ""; i++) {
			nm = pkg[i];
			if (nm in inst || nm in preinst) {

				remdis = ""
				if (nm in preinst && ! (nm in inst)) { # pre-installed uninstalled
					remdis = "disabled"
				} else if (nm in preinst && nm in inst) { # pre-installed updated
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

					if (system("ipkg -V0 compare_versions " v " \">\" " ver[uinst[nm]]))
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
			print "<tr><td colspan=2><strong>Update all installed</strong></td> \
				<td><input type=submit name=updateall value=UpdateAll></td></tr>"

		print "</table></fieldset> \
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
		</table></fieldset>", pkgfeed)
		}
	}'
fi

echo "</form></body></html>"
