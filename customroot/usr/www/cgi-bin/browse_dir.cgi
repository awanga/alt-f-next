#!/bin/sh

# recursive function to transverse directories. FIXME -- it is tooo slooow
# $1-start directory $2-path of end directory
transverse() {
	local sp
	sp="${sp}&emsp;"

	start=$1
	dir="$(echo $2 | cut -d'/' -f1)"	# $2 can't start with /
	end="$(echo $2 | cut -d'/' -f2-)"

#	echo "1=$1 2=$2 start=$start dir=$dir end=$end"

	a="$(find $start -maxdepth 1 -type d 2>/dev/null | sort -d | tr '\n' ';')"

	IFS=";"
	for i in $a; do
		bn=$(basename $i)
		if test "$i" != "$start"; then
			eval $(ls -ld "$i" | awk '{printf "user=%s; group=%s; perm=%s", $3, $4, substr($1,2)}')
			echo "<tr><td><a style=\"text-decoration: none\" href=\"/cgi-bin/browse_dir.cgi?${url_op}${url_srcdir}${url_wind}${url_id}browse=${i}\">${sp}$bn</a></td>
				<td>$user</td><td>$group</td><td><font face=Courier>$perm</font></td></tr>"
		fi
		if test "$bn" = "$dir" -a -d $start/$dir; then
			transverse $start/$dir "$end"
		fi
	done
}

. common.sh
check_cookie

hdr="Folders Browse"

if test -n "$(echo "$QUERY_STRING" | grep 'wind=no')"; then	
	ok_sel="disabled"
	write_header "$hdr"
else
	html_header "$hdr"
	mktt() { # no tooltips...
		true
	}
	echo "<center><h2>$hdr</h2></center>"
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

eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
	awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')

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
	url_srcdir="srcdir=$(httpd -d $srcdir)?"
	srcdir="$(httpd -d $srcdir)"
fi

#echo "<pre>$(set)</pre>"

#if test -h "$browse"; then
	browse=$(readlink -f "$browse")
#fi

if ! echo "$browse" | grep -q '^/mnt'; then
	echo "<h3>Warning: Folder base must be /mnt</h3>"
	browse="/mnt"
elif ! test -d "$browse"; then
	echo "<h3>Warning: Folder \"$browse\" does not exist.</h3>"
	browse="/mnt"
fi

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
	<td><input type=text name=newdir value="$browse" $(ttip curdir)></td>
	<td><input type=submit $ok_sel value=OK onclick="ret_val('$id', '$browse')"></td>
	<td><input type=submit $ok_sel value=Cancel onclick="window.close()"></td>
	<td><input type=button value=Permissions $(ttip perms) onclick="perms('$browse')"></td>
	</tr>

	<tr><td></td>
	<td colspan=5>
		<input type=button name=copyDir value=Copy $(ttip cpdir) onclick="ops('Copy','$browse','$url_id','$url_wind')">
		<input type=button name=copyDirContent value=CopyContent $(ttip cpdircont) onclick="ops('CopyContent','$browse','$url_id','$url_wind')">
		<input type=button name=cutDir value=Cut  $(ttip cutdir) onclick="ops('Move','$browse','$url_id','$url_wind')">
		<input type=hidden name=op value="$op">
		<input type=hidden name=srcdir value="$srcdir">
		<input type=submit name=PasteDir value=Paste  $(ttip pastedir) onclick="return op_paste('$op','$srcdir','$browse')">
		<input type=submit name=CreateDir value=Create $(ttip mkdir)>
		<input type=submit name=DeleteDir value=Delete $(ttip rmdir) onclick="return confirm('Remove folder $browse and all its files and sub-folders?')">
	</td>
	</tr></table></form>

	<br><table><tr><td>
		<strong>$browse</strong></td>
		<td><strong>Owner</strong></td>
		<td><strong>Group</strong></td>
		<td><strong>Permissions</strong></td></tr>
EOF

transverse /mnt "$(echo $browse | cut -d/ -f3-)"

echo "</table></body></html>"
