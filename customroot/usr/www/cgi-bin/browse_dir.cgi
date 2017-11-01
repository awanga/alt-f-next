#!/bin/sh

# spaces at pathnames end are not properly handled 
# as QUERY_STRING doesn't has them (busybox httpd bug?) 
# also 'basename' and 'dirname' strips all but one leading/trailing space

# there is url-encode, for URLs, that use %<2hex>
# there are http-entities (either &<entity>; or &#<number>;) for html text
# text is UTF-8, multibyte for > 127, need to convert to UCS-2 and code 2 bytes as a single entity

tree() {
	echo "<table><tr><th align=left>&emsp;Folder</th><th>Owner</th><th>Group</th><th>Permissions</th></tr>"
	traverse /mnt "$(echo $1 | cut -d/ -f3-)"
}

# recursive function to traverse directories.
# $1-start directory $2-path of end directory
traverse() {
	local sp
	sp="${sp}&emsp;"

	start="$1"
	dir=$(echo "$2" | cut -d'/' -f1)	# $2 can't start with /
	end=$(echo "$2" | cut -d'/' -f2-)

	a=$(find "$start" -maxdepth 1 -type d 2>/dev/null | tail +2 | sort -d)

	turl="<tr><td><a class=\"nodecor\"
	    href=\"/cgi-bin/browse_dir.cgi?${url_wind}${url_id}${url_vmode}${url_op}${url_srcdir}browse"

	IFS="
"
	for i in $a; do
		bn=$(basename "$i")
		if test ${bn:0:1} = "." -o "$bn" = "lost+found"; then continue; fi

		tbn=$(http_encode "$bn")
		tbi=$(url_encode "$i")

		eval $(ls -ld "$i" | awk '{printf "user=%s; group=%s; perm=%s", $3, $4, substr($1,2)}')
		echo "$turl=${tbi}\">${sp}${tbn}</a></td>
			<td>$user</td><td>$group</td><td class=\"monospace\">$perm</td></tr>"
		if test "$bn" = "$dir" -a -d "$start/$dir"; then
			traverse "$start/$dir" "$end"
		fi
	done
}

# flat view of directories
# $1-path of end directory
flat() {
	turl="<a class=\"nodecor\"
		href=\"/cgi-bin/browse_dir.cgi?${url_wind}${url_id}${url_vmode}${url_op}${url_srcdir}browse"

	echo "<strong>Folder:</strong> "
	i=2
	while true; do
		tp=$(echo "$1" | cut -d/ -f$i)
		acc="$acc/$tp"
		if test -z "$tp"; then break; fi
		#if test "$tp" = "$ep"; then break; fi

		tp=$(http_encode "$tp")
		tacc=$(url_encode "$acc")

		echo -n "$turl=$tacc\">/$tp</a>"
		i=$((i+1))
	done

	echo " (hit path component to visit it)"
	echo "<table><tr><th align=left></th><th>Owner</th><th>Group</th><th>Permissions</th></tr>"

	a=$(find "$1" -maxdepth 1 -type d 2>/dev/null | tail +2 | sort -d)
	turl="<tr><td><a class=\"nodecor\"
	    href=\"/cgi-bin/browse_dir.cgi?${url_wind}${url_id}${url_vmode}${url_op}${url_srcdir}browse"

	t=$(dirname "$1")
	t=$(url_encode "$t")
	echo "$turl=$t\"><em>Up Folder</em></a></td><td colspan=4></td></tr>"

	IFS="
"
	for i in $a; do
		bn=$(basename "$i")
		#if test ${bn:0:1} = "." -o "$bn" = "lost+found"; then continue; fi
		if test "$bn" = "lost+found"; then continue; fi

		tbn=$(http_encode "$bn")
		tbi=$(url_encode "$i")

		eval $(ls -ld "$i" | awk '{printf "user=%s; group=%s; perm=%s", $3, $4, substr($1,2)}')
		echo "$turl=${tbi}\">${tbn}</a></td>
			<td>$user</td><td>$group</td><td class=\"monospace\">$perm</td></tr>"
	done
	
}

. common.sh
check_cookie

if test -n "$QUERY_STRING"; then
	parse_qstring
fi

hdr="Folders Browse"

LOCAL_STYLE='
.nodecor { text-decoration: none; }
.monospace { font-family: courier; }
'

if test "$wind" = "no"; then
	ok_sel="disabled"
	write_header "$hdr"
else
	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		hlp="<a href=\"../$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi

	html_header "$hdr $hlp"
	mktt() { # no tooltips...
		true
	}
fi

has_disks

mktt curdir "The currently selected folder.<br>
Can be edited to create or rename a folder using the Create or Rename buttons."
mktt cpdir "Mark the currently selected folder for copying."
mktt cpdircont "Mark the currently selected folder contents (not the folder itself) for copying."
mktt cutdir "Mark the currently selected folder for moving."
mktt pastedir "Paste the previously marked folder into the currently selected folder."
mktt mkdir "Create a folder with the name present in the edited Selected field."
mktt mvdir "Rename the currently selected folder to the edited name in the Selected field."
mktt rmdir "Delete the currently selected folder."
mktt perms "Change permissions and ownership of the currently selected folder."

if test -n "$wind"; then url_wind="wind=${wind}?"; fi

if test -n "$id"; then url_id="id=${id}?"; fi

if test -n "$op"; then url_op="op=${op}?"; fi

if test "$vmode" = "tree"; then
	url_vmode="vmode=tree?"
	tree_sel=checked
else
	url_vmode="vmode=flat?"
	flat_sel=checked
fi

if test -n "$srcdir"; then
	perce_srcdir=$srcdir
	url_srcdir="srcdir=${perce_srcdir}?"
	srcdir=$(httpd -d "$srcdir")
	urle_srcdir=$(http_encode "$srcdir")
fi

if test -n "$browse"; then
	perce_browse=$browse
	browse=$(httpd -d $browse)
	dece_browse=$(http_encode "$browse")

	if ! test -d "$browse"; then
		echo "<h3 class="warn">Warning: Folder \"$dece_browse\" does not exists.</h3>"
	fi

	while ! readlink -f "$browse" >& /dev/null; do
		browse=$(dirname "$browse")
	done
	browse=$(readlink -f "$browse")
fi

if ! echo "$browse" | grep -q '^/mnt'; then
	echo "<h3 class="warn">Warning: Only sub folders of /mnt are allowed.</h3>"
	browse="/mnt"
	dece_browse=$(http_encode "$browse")
	perce_browse=$(url_encode "$browse")
fi

if test "$(realpath /Alt-F 2> /dev/null)" = "$browse"; then
	echo "<h3 class="warn">Warning: The Alt-F folder should not be manipulated.</h3>"
	browse=$(dirname "$browse")
	dece_browse=$(http_encode "$browse")
	perce_browse=$(url_encode "$browse")
fi

fop_dis=""
fop=$(ls /tmp/folders_op.* 2> /dev/null)
if test -f "$fop"; then
	fpid=$(echo $fop | sed "s|/tmp/folders_op.\(.*\)|\1|")
	if kill -0 $fpid >& /dev/null; then
		fop_dis="disabled"
		fop_msg='<tr><td></td><td class="red">Folder operation currently in progress</td></tr>'
	else
		rm -f $fop
	fi
fi

if test -z "$ok_sel"; then
	ok_cancel="<input type=submit value=OK onclick=\"ret_val('$id', '$dece_browse')\">
		<input type=submit value=Cancel onclick=\"window.close()\">"
fi

#debug

cat <<-EOF
	<script type="text/javascript">
		function ret_val(inp, adir) {
			window.opener.document.getElementById(inp).value = adir;
			window.close();
		}
		function renameask(dir) {
			edir = window.decodeURIComponent(dir);
			document.getElementById("oldname").value = edir;
			return true
		}
		function deleteask(dir) {
			edir = window.decodeURIComponent(dir);
			if (edir == "/mnt") {
				alert("Refusing to delete all disks data!")
				return false
			}
			if (edir.charAt(edir.length-1) == "/")
				edir = edir.substr(0, edir.length-2)
			pcomp = edir.split("/")
			if (pcomp.length == 3)
				return confirm("ARE YOU REALLY SURE THAT YOU WANT TO DELETE ALL THE\n\n   " 
+ pcomp[2] + "\n\nFILESYSTEM DATA? REALLY?")
			return confirm("Delete folder\n\n   " + edir + "\n\nand all its files and sub-folders?");
		}
		function vmode(mode, dir) {
			window.location.assign("/cgi-bin/browse_dir.cgi?${url_wind}${url_id}${url_op}vmode=" + mode + "?${url_srcdir}browse=" + dir)
		}
		function perms(dir) {
			window.location.assign("/cgi-bin/perms.cgi?${url_wind}browse=" + dir)
		}
		function ops(op, dir, id, wind) {
			//edir = window.encodeURIComponent(dir);
			window.location.assign("/cgi-bin/browse_dir.cgi?" +
wind + id + "op=" + op + "?srcdir=" + dir + "?browse=" + dir) 
		}
		function op_paste(op, srcdir, destdir) {
			srcdir = window.decodeURIComponent(srcdir);
			destdir = window.decodeURIComponent(destdir);
			ret = false;
			if ( op == "")
				alert("No copy or move operation has been previously selected.")
			else if (destdir == "" || srcdir == "")
				alert("No source or destination folder has been selected.")
			else if (srcdir == destdir)
				alert("Source and destination folder are the same.")
			else if (op == 'Move')
				msg = "Move folder"	
			else if (op == 'Copy')
				msg = "Copy folder"	
			else if (op == 'CopyContent')
				msg = "Copy all files and folders from"	

			ret = confirm(msg + "\n\n   " + srcdir + "\n\nto\n\n   " +
				 destdir + "\n\nThis operation can take a long time to accomplish,\n" +
				"depending on the amount of data to transfer.\n\nProceed?")
			return ret
		}
	</script>

	<form action="/cgi-bin/dir_proc.cgi" method="post">
	<table><tr>
		<th>Selected: </th>
		<td colspan=4><input type=text size=30 id=newdir name=newdir value="$dece_browse" $(ttip curdir)></td>
		</tr>$fop_msg<tr><td></td><td>

		<input type=button $fop_dis name=copyDir value=Copy $(ttip cpdir) onclick="ops('Copy','$perce_browse','$url_id','$url_wind')">
		<input type=button $fop_dis name=copyDirContent value=CopyContent $(ttip cpdircont) onclick="ops('CopyContent','$perce_browse','$url_id','$url_wind')">
		<input type=button $fop_dis name=cutDir value=Cut $(ttip cutdir) onclick="ops('Move','$perce_browse','$url_id','$url_wind')">
		<input type=submit  $fop_dis name=PasteDir value=Paste $(ttip pastedir) onclick="return op_paste('$op','$perce_srcdir','$perce_browse')">

	</td></tr><tr><td></td><td>
		<input type=submit $fop_dis name=CreateDir value=Create $(ttip mkdir)>
		<input type=submit $fop_dis name=DeleteDir value=Delete $(ttip rmdir) onclick="return deleteask('$perce_browse')">
		<input type=submit $fop_dis name=RenameDir value=Rename $(ttip mvdir) onclick="return renameask('$perce_browse')">
		<input type=button value=Permissions $(ttip perms) onclick="perms('$perce_browse')">
	</td></tr><tr>
		<td></td><td>$ok_cancel View: Tree<input type=radio $tree_sel onclick="vmode('tree','$perce_browse')">
			Flat<input type=radio $flat_sel onclick="vmode('flat','$perce_browse')"></td></table><p>
		<input type=hidden name=op value="$op">
		<input type=hidden name=srcdir value="$urle_srcdir">
		<input type=hidden name=oldname id=oldname value="">
	</form>
EOF

set -f # avoid pathname expansion, or '?' and '*' in filenames will be expanded!
if test "$vmode" = "tree"; then
	tree "$browse"
else
	flat "$browse"
fi

echo "</table></body></html>"
