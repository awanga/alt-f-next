#!/bin/sh

. common.sh
check_cookie

hdr="Folder Ownership and Access Permissions"

if test -n "$QUERY_STRING"; then
	parse_qstring
fi

if test "$wind" = "no"; then
	write_header "$hdr"
else
	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		hlp="<a href=\"../$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi

	html_header "Folder Ownership and Access Permissions $hlp"
	mktt() { # no tooltips or help...
		true
	}
fi

browse="$(httpd -d $browse)"
esc_browse=$(httpd -e "$browse")

# get the fs type
tmp="$browse"
while ! mountpoint -q "$tmp"; do
	tmp=$(dirname "$tmp")
done

if test "$tmp" != "/"; then
	TYPE=$(grep $tmp /proc/mounts | cut -d" " -f3)

	if test "$TYPE" != "ext2" -a "$TYPE" != "ext3" -a "$TYPE" != "ext4" -a "$TYPE" != "nfs"; then
		cat<<-EOF
			<h4 class="warn">Filesystem is of type $TYPE, not a linux native filesystem.<br>
			Only ext2, ext3, ext4 or NFS filesystems can use UNIX permissions.
			</h4>$(back_button)</body></html>
		EOF
	exit 0
	fi
fi

echo "$browse" | grep -q '^/mnt'
if test "$?" = 1; then
	echo "<h3>Warning: Folder base must be /mnt</h3>"
	browse="/mnt"
elif ! test -d "$browse"; then
	echo "<h3>Warning: Folder \"$esc_browse\" does not exists.</h3>"
	browse="/mnt"
fi

eval $(ls -ldL "$browse" | awk '{
	printf "usero=%s; groupo=%s; ", $3,$4
	for (i=2; i<=length($1); i++) {
		key = substr($1,i,1)
		if (key == "r" || key == "w" || key == "x" || key == "s")
			printf "p%d=checked; ", i
		if ((key == "s" || key == "S") && i == 7)
			print "GIDCHK=checked"
	}
}')

OIFS="$IFS"; IFS=":"

while read user upass uid ugid uname dir shell;do
	if test "${user:0:1}" = "#" -o -z "$user" -o -z "$uid" -o -z "$uname"; then continue; fi
	#if test $shell = "/bin/false"; then continue; fi
	#if test $uid -lt 100; then continue; fi
	if test "$usero" = "$user"; then sel=selected; else sel=""; fi
	users="$users <option $sel value=$user>$uname</option>"
done < /etc/passwd

while read group gpass ggid userl;do
	if test "${group:0:1}" = "#" -o "$gpass" = "!"; then continue; fi
	#if test $ggid -lt 100; then continue; fi
	if test "$groupo" = "$group"; then sel=selected; else sel=""; fi
	groups="$groups <option $sel>$group</option>"
done < /etc/group

IFS="$OIFS"

cat <<-EOF
	<form action="/cgi-bin/dir_proc.cgi" method="post">
	<table>
	<tr><th colspan=2 align=left><em>$(basename "$browse"):</em></th><th>Can Read</th><th>Can Write</th><th>Can Browse</th></tr>
	<tr align=center>
		<td align=left><strong>Owner</strong></td>
		<td align=left><select name=nuser>$users</select></td>
		<td><input type=checkbox $p2 name=p2 value="r"></td>
		<td><input type=checkbox $p3 name=p3 value="w"></td>
		<td><input type=checkbox $p4 name=p4 value="x"></td>
	</tr><tr align=center>
		<td align=left><strong>Users in group</strong></td>
		<td align=left><select name=ngroup>$groups</select></td>
		<td><input type=checkbox $p5 name=p5 value="r"></td>
		<td><input type=checkbox $p6 name=p6 value="w"></td>
		<td><input type=checkbox $p7 name=p7 value="x"></td>
	</tr><tr align=center>
		<td align=left><strong>Other users</strong></td>
		<td></td>
		<td><input type=checkbox $p8 name=p8 value="r"></td>
		<td><input type=checkbox $p9 name=p9 value="w"></td>
		<td><input type=checkbox $p10 name=p10 value="x"></td>
	</tr></table><p><table>
	<tr><td colspan=2>Make new files/folders inherit the group ownership</td><td><input type=checkbox $GIDCHK name=setgid value=yes></td></tr>
	<tr><td colspan=2>Apply recursively to sub-folders</td><td><input type=checkbox name=recurse value=yes></td></tr>
	<tr><td colspan=2>Apply also to files</td><td><input type=checkbox name=toFiles value=yes></td></tr>
	</table>
	<p><input type=submit name=Permissions value="Submit">$(back_button)
	<input type=hidden name=newdir value="$browse">
	<input type=hidden name=goto value="$HTTP_REFERER">
	</form></body></html>
EOF
