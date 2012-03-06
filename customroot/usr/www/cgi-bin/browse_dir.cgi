#!/bin/sh

# recursive function to transverse directories.
# $1-start directory $2-path of end directory
transverse() {
	local sp
	sp="${sp}&emsp;"

	start=$1
	dir=$(echo "$2" | cut -d'/' -f1)	# $2 can't start with /
	end=$(echo "$2" | cut -d'/' -f2-)

#echo "<tr><td>1=\"$1\" 2=\"$2\" start=\"$start\" dir=\"$dir\" end=\"$end\"</td></tr>"

	a=$(find "$start" -maxdepth 1 -type d 2>/dev/null | tail +2 | sort -d | tr '\n' ';')

	IFS=";"
	for i in $a; do
		bn=$(basename "$i")
		tbn=$(httpd -e "$bn")
		tbi=$(httpd -e "$i")
		eval $(ls -ld "$i" | awk '{printf "user=%s; group=%s; perm=%s", $3, $4, substr($1,2)}')
			echo "<tr><td><a style=\"text-decoration: none\" 
	href=\"/cgi-bin/browse_dir.cgi?${url_op}${url_srcdir}${url_wind}${url_id}browse=${tbi}\">${sp}${tbn}</a></td>
	<td>$user</td><td>$group</td><td style="font-family:courier">$perm</td></tr>"
		if test "$bn" = "$dir" -a -d "$start/$dir"; then
			transverse "$start/$dir" "$end"
		fi
	done
}

. common.sh
check_cookie

if test -n "$QUERY_STRING"; then
	parse_qstring
fi

hdr="Folders Browse"

if test "$wind" = "no"; then
	ok_sel="disabled"
	write_header "$hdr"
else
	html_header "$hdr"
	mktt() { # no tooltips...
		true
	}
	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		hlp="<a href=\"../$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi

	echo "<center><h2>$hdr $hlp</h2></center>"
fi

mktt curdir "The currently selected folder.<br>
Can be edited to create a folder using the Create button bellow."
mktt cpdir "Mark the above selected folder for copying."
mktt cpdircont "Mark the above selected folder contents (not the folder itself) for copying."
mktt cutdir "Mark the above selected folder for moving."
mktt pastedir "Paste the previously marked folder into the above selected folder."
mktt mkdir "Create the folder whose name is in the above field."
mktt rmdir "Delete the above selected folder."
mktt perms "Change permissions and ownership of the selected folder."

if test -n "$browse"; then
	browse="$(httpd -d $browse)"
fi

if test -n "$wind"; then
	url_wind="wind=${wind}?"
fi

if test -n "$id"; then
	url_id="id=${id}?"
fi

if test -n "$op"; then
	url_op="op=${op}?"
fi

if test -n "$srcdir"; then
	srcdir=$(httpd -d $srcdir)
	esc_srcdir=$(httpd -e "$srcdir")
	url_srcdir="srcdir=${esc_srcdir}?"
fi

#debug

browse=$(readlink -f "$browse")

if ! echo "$browse" | grep -q '^/mnt'; then
	browse="/mnt"
elif ! test -d "$browse"; then
	echo "<h3>Warning: Folder \"$browse\" does not exist.</h3>"
	browse="/mnt"
fi

esc_browse=$(httpd -e "$browse")

cat <<-EOF
	<script type="text/javascript">
		function ret_val(inp, adir) {
			window.opener.document.getElementById(inp).value = adir;
			window.close();
		}
		function perms(dir) {
			window.location.assign("/cgi-bin/perms.cgi?${url_wind}browse=" + dir)
		}
		function ops(op, dir, id, wind) {
			window.location.assign("/cgi-bin/browse_dir.cgi?" +
wind + id + "browse=" + dir + "?op=" + op + "?srcdir=" + dir)
		}
		function op_paste(op, srcdir, destdir) {
			ret = false;
			if ( op == "")
				alert("No copy or move operation has been previously selected.")
			else if (destdir == "" || srcdir == "")
				alert("No source or destination folder has been selected.")
			else if (srcdir == destdir)
				alert("Source and destination folder are the same.")
			else if (op == 'Copy')
				msg = "Copy folder"	
			else if (op == 'CopyContent')
				msg = "Copy all files and folders from"	

			ret = confirm(msg + '\n\n' +
"   " + srcdir + '\n' + "to" + '\n' + "   " + destdir + '\n\n' +
"This operation can take a long time to accomplish," + '\n' +
"depending on the amount of data to " + op + '\n\n' + "Proceed?")
			return ret
		}
	</script>

	<form action="/cgi-bin/dir_proc.cgi" method="post">
	<table><tr>
		<td>Selected: </td>
		<td colspan=4><input type=text size=30 name=newdir value="$esc_browse" $(ttip curdir)></td>
		<td><input type=submit $ok_sel value=OK onclick="ret_val('$id', '$esc_browse')"></td>
		<td><input type=submit $ok_sel value=Cancel onclick="window.close()"></td>
	</tr><tr><td></td><td>
		<input type=button name=copyDir value=Copy $(ttip cpdir) onclick="ops('Copy','$esc_browse','$url_id','$url_wind')">
		<input type=button name=copyDirContent value=CopyContent $(ttip cpdircont) onclick="ops('CopyContent','$esc_browse','$url_id','$url_wind')">
		<input type=button name=cutDir value=Cut $(ttip cutdir) onclick="ops('Move','$esc_browse','$url_id','$url_wind')">
		<input type=submit name=PasteDir value=Paste $(ttip pastedir) onclick="return op_paste('$op','$esc_srcdir','$esc_browse')">
	</td></tr><tr><td></td><td>
		<input type=submit name=CreateDir value=Create $(ttip mkdir)>
		<input type=submit name=DeleteDir value=Delete $(ttip rmdir) onclick="return confirm('Remove folder $esc_browse and all its files and sub-folders?')">
		<input type=button value=Permissions $(ttip perms) onclick="perms('$esc_browse')">
	</td></tr></table>
		<input type=hidden name=op value="$op">
		<input type=hidden name=srcdir value="$esc_srcdir">
	</form>

	<br><table><tr><th></th><th>Owner</th><th>Group</th><th>Permissions</th></tr>
EOF

transverse /mnt "$(echo $browse | cut -d/ -f3-)"

echo "</table></body></html>"
