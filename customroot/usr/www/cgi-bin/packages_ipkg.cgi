#!/bin/sh
. common.sh

check_cookie
write_header "Alt-F Package Manager"

#debug

if ! ipkg status >/dev/null; then
	has_disks

	cat<<-EOF
		<h4>No ipkg instalation found, install ipkg in:</h4>
		<form action="/cgi-bin/packages_ipkg_proc.cgi" method=post>
	EOF
	select_part
	echo "</select><input type=submit name=install value=Install>
	</form></body></html>"

else

	feed=$(awk '/^src /{print $3}' /etc/ipkg.conf)

	ipkg-cl -V0 info | awk -v confeeds="$feed" '
	BEGIN {
		nfeeds = split(confeeds, feeds);
	}
	/Package:/ { i++; nm=$2; pkg[i] = nm } # this relies on Package being the first field 
	/Version:/ { ver[i] = $2 } 
	/Source:/ { url[i] = $2 } 
	/Description:/ { des[i] = substr($0, index($0,$2)) } 
	/Status:/ { if ($4 == "installed")
			inst[nm] = i;
		else { uinst[nm] = i; ucnt++;}
	}  
	END {
		printf "<form action=\"/cgi-bin/packages_ipkg_proc.cgi\" method=post> \
			<fieldset><legend><strong> Configure Feeds </strong></legend> \
			<input type=hidden name=nfeeds value=%d><table>", nfeeds
		for (i=1; i<=nfeeds; i++) 
			printf "<tr><td>Feed %d:</td><td><input type=text size=50 name=feed_%d value=%s></td></tr>", i, i, feeds[i];
		print "<tr><td></td><td><input type=submit name=changeFeed value=ChangeFeed> \
			<input type=submit name=defaultFeed value=DefaultFeed></td></tr></table><br> \
			<strong>Update package list:</strong><input type=submit name=updatelist value=UpdateList> \
			</fieldset><br> \
			<fieldset><legend><strong> Installed Packages </strong></legend> \
			<table><tr> \
				<th>Name</th><th>Version</th><th></th><th></th><th>Description</th> \
			</tr>"

		update = 0;
		for (i=1; pkg[i] != ""; i++) {
			nm = pkg[i];
			if (nm in inst) {
				if (nm in uinst) {	# new version available, old has missing info
					j = uinst[nm]; v = ver[inst[nm]]; update++;
					upd=sprintf("<td><input type=submit name=%s value=Update></td>", nm);
					delete uinst[nm]; ucnt--; delete inst[nm];
				} else {
					j = i; v = ver[i];
					upd="<td></td>";
				}
				printf "<tr><td><a href=\"%s\">%s</a></td><td>%s</td>",
					url[j], nm, v;
				printf "<td><input type=submit name=%s value=Remove></td>", nm;
				print upd;
				printf "<td>%s</td></tr>\n\n", des[j];
			}
		}
	
		print "<tr><td><br></td></tr>"
		if (update != 0)
			print "<tr><td colspan=2><strong>UpdateAll</strong></td> \
				<td><input type=submit name=updateall value=UpdateAll></td></tr>"

		print "<script type=\"text/javascript\"> \
				function ask() { \
					return confirm(\"All files and configurations will be erased. You will have to reinstall ipkg on a disk partition.\"); \
				} \
			</script> \
			<tr><td colspan=2><strong>Remove all installed</strong></td> \
				<td><input type=submit name=removeall value=RemoveAll onclick=\"return ask()\"></td></tr> \
			</table></fieldset> \
			<br><fieldset><legend><strong> Available Packages </strong></legend><table>"

		if (ucnt == 0) {
			print "None"
		} else {
			print "<tr><th>Name</th><th>Version</th> \
				<th></th><th>Description</th></tr>"

			for (i=1; pkg[i] != ""; i++) {
				nm = pkg[i];
				if (nm in uinst) {
					printf "<tr><td><a href=\"%s\">%s</a></td><td>%s</td>",
					url[i], nm, ver[i];
					printf "<td><input type=submit name=%s value=Install></td>", nm;
					printf "<td>%s</td></tr>\n\n", des[i];
				}
			}
		printf ("<tr><td><br></td></tr><tr><td colspan=2><strong>Install all available</strong></td> \
			<td><input type=submit name=installall value=InstallAll></td></tr>\
		</table></fieldset></form>", pkgfeed)
		}
	}'

fi
