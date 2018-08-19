#!/bin/sh

. common.sh
check_cookie

LOCAL_STYLE='.dim {background-color: #dddddd;}'
write_header "New User Setup"

check_https

CONFP=/etc/passwd

has_disks

if ! test -h /home -a -d "$(readlink -f /home)"; then
	cat<<-EOF
		<h4>No users folder found, create it in:</h4>
		<form action="/cgi-bin/newuser_proc.cgi" method=post>
	EOF
	# FIXME offer possibility of creation of Public Folders
	select_part
	echo "<input type=submit name=create_dir value=CreateDir>
		</form></body></html>"
	exit 0
fi

mktt ttuname "Full user name. Used as login name on MS"
mktt ttnick	"User nick name, only letters and digits. Used as login name on linux"
mktt ttuid	"User id, should be greater than 99. Change only if revelant for NFS"
mktt ttgid "Main users group id, should be greater than 99. Change only if revelant for NFS"
mktt ttpass "User password. Used as password on linux and MS"
mktt ttpassa "Repeat the entered password above."

cat <<EOF
	<script type="text/javascript">
	function upnick() {
		nm = document.frm.uname.value;
		snm = nm.split(" ");
		document.frm.nick.value = 
			snm[0].substr(0,4).toLowerCase() + 
			snm[snm.length - 1].substr(0,4).toLowerCase();
	}
	function pcheck() {
		if (document.frm.pass.value.length == 0 || document.frm.pass.value != document.frm.passa.value) {
			alert("Password checking failed, try again");
			document.frm.pass.value="";
			document.frm.passa.value="";
			return false; // this is not avoiding the form action to be executed, why?
 		} else
			return true;
	}
	</script>
EOF

parse_qstring

#debug

if test "$act" = "changepass"; then
	uname=$(httpd -d "$uname")
	if ! id -u "$nick" >& /dev/null; then msg "User doesn't exists."; fi
	uid=$(id -u "$nick")
	gid=$(id -g "$nick")
	chpass="readonly"
	subbut='<input type="submit" name="chpass" value="ChangePass">'

#elif test "$act" = "newuser"; then
else
	cat<<-EOF
		<script type="text/javascript">
		setTimeout("upnick()", 500) // hack, the form is not yet created
		</script>
	EOF

	eval $(awk -F: '{ if ($3 > uid) uid=$3}
		{ if ($4 > gid) gid=$4}
		END { if (uid < 1000) uid=999; gid=100; printf "uid=%d; gid=%d", uid+1, gid}' $CONFP)

	chpass=""
	subbut='<input type="submit" name="submit" value="Submit">'
fi

cat <<EOF
	<form name=frm action="/cgi-bin/newuser_proc.cgi" method="post">
	<table>
	<tr><td>Full name</td><td><input type=text $chpass name=uname value="$uname" onChange="upnick()" $(ttip ttuname)></td></tr>
	<tr><td>Nick name<td><input type=text $chpass name=nick value="$nick" $(ttip ttnick)></td></tr>
	<tr><td>User id<td><input class="dim" type=text $chpass name=uid value="$uid" $(ttip ttuid)></td></tr>
	<tr><td>Group id<td><input class="dim" type=text $chpass name=gid value="$gid" $(ttip ttgid)></td></tr>
	<tr><td>Password<td><input type=password name=pass $(ttip ttpass)></td></tr>
	<tr><td>Again<td><input type=password name=passa $(ttip ttpassa)></td></tr>
	</table><p>
	$subbut <input type="submit" name="cancel" value="Cancel"></td></tr>
	</form></body></html>
EOF
