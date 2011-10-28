#!/bin/sh

. common.sh
check_cookie

hdr="Directory Ownership and Access Permissions"

if test -n "$(echo "$QUERY_STRING" | grep 'wind=no')"; then	
	write_header "$hdr"
else
	html_header
	mktt() { # no tooltips or help...
		true
	}
	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		#hlp="<a href=\"http://$HTTP_HOST/$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
		hlp="<a href=\"$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi

	echo "<center><h2>Directory Ownership and Access Permissions $hlp</h2></center>"
fi

#echo "<pre>$(set)</pre>"
#echo QUERY_STRING=$QUERY_STRING

if test -z "$QUERY_STRING"; then	
	echo "</body></html>"
	exit 0
fi

eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
	awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')

browse="$(httpd -d $browse)"

# get the fs type
tmp="$browse"
while ! mountpoint -q "$tmp"; do
	tmp=$(dirname "$tmp")
done
#eval $(blkid -s TYPE $(mountpoint -n $tmp | cut -d' ' -f1) | cut -d' ' -f2)
TYPE=$(grep $tmp /proc/mounts | cut -d" " -f3)
if test "$TYPE" != "ext2" -a "$TYPE" != "ext3" -a "$TYPE" != "ext4" -a "$TYPE" != "nfs"; then
	cat<<-EOF
		<h3><font color=blue>
			Filesystem is of type $TYPE, not a linux native filesystem.<br>
			Only ext2, ext3, ext4 or NFS filesystems can use UNIX permissions.
		</font></h3>$(back_button)</body></html>
	EOF
	exit 0
fi

echo "$browse" | grep -q '^/mnt'
if test "$?" = 1; then
	echo "<h3>Warning: Directory base must be /mnt</h3>"
	browse="/mnt"
elif ! test -d "$browse"; then
	echo "<h3>Warning: Directory \"$browse\" does not exista.</h3>"
	browse="/mnt"
fi

eval $(ls -ldL "$browse" | awk '{
	printf "usero=%s; groupo=%s; ", $3,$4
	for (i=2; i<=length($1); i++) {
		key = substr($1,i,1)
		if (key == "r" || key == "w" || key == "x" || key == "s")
			printf "p%d=checked; ", i
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
	<table><!--caption><h3>$browse</h3></caption-->
	<tr align=center><th colspan=2 align=left><em>$(basename "$browse"):</em></th><th>Can Read</th><th>Can Write</th><th>Can Browse</th></tr>
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
	</tr>
	<tr><td><br></td></tr>
	<tr><td colspan=2>Apply recursively to subdirectories</td><td><input type=checkbox name=recurse value=yes></td></tr>
	<tr><td colspan=2>Apply ownership also to files</td><td><input type=checkbox name=toFiles value=yes></td></tr>
	<tr><td><br></td></tr>
	<tr><td></td><td colspan=2>$(back_button)<input type=submit name=Permissions value="Submit"></td></tr>
	</table>
	<input type=hidden name=newdir value="$browse">
	<input type=hidden name=goto value="$HTTP_REFERER">
	</form></body></html>
EOF
