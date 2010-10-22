#!/bin/sh

. common.sh
check_cookie
write_header "New User Setup"

CONFP=/etc/passwd

if test -f /tmp/firstboot; then
	cat<<-EOF
		<center>
		<h3>Welcome to your first login to Alt-F</h3>
		<h4>To continue setting up Alt-F, you should now specify</h4>
		 <h4>the disk partition where users will store their data</h4>
		</center>
	EOF
fi

has_disks

if ! test -h /home -a -d "$(readlink -f /home)"; then
	cat<<-EOF
		<h4>No users directory found, create it in:</h4>
		<form action="/cgi-bin/newuser_proc.cgi" method=post>
	EOF
	# FIXME offer possibility of creation of Public directories
	select_part
	echo "</select><input type=submit name=create_dir value=CreateDir>
		</form></body></html>"
	exit 0
fi

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

eval $(awk -F: '{if ($3 > uid) uid=$3} END{ 
	printf "uid=%d", uid}' $CONFP)

if test -z "$QUERY_STRING"; then
	if test "$uid" -lt 1000; then uid=1000; fi
else
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
		printf "%s=%c%s%c\n",$1,39,$2,39}')
	uname="$(httpd -d "$uname")"
	chpass="readonly"
	if test -z "$nick"; then
		cat<<-EOF
			<script type="text/javascript">
			setTimeout("upnick()", 500) // hack, the form is not yet created
			</script>
		EOF
		chpass=""
		if test "$uid" -lt 1000; then uid=999; fi
		uid=$((uid+1))
	fi
fi

# FIXME add gid support!
gid="not_yet"

cat <<EOF
	<!--form name=frm action="/cgi-bin/newuser_proc.cgi" method="post" onSubmit="pcheck()"-->
	<form name=frm action="/cgi-bin/newuser_proc.cgi" method="post">
	<fieldset><legend><strong>User Details</strong></legend>
	<table>
	<tr><td>Full name</td><td><input type=text $chpass name=uname value="$uname" onChange="upnick()"></td></tr>
	<tr><td>Nick name<td><input type=text $chpass name=nick value=$nick></td></tr>
	<tr><td>User id<td><input type=text $chpass name=uid value=$uid></td></tr>
<!--	<tr><td>Group id<td><input type=text $chpass name=gid value=$gid></td></tr> -->
	<tr><td>Password<td><input type=password name=pass></td></tr>
	<tr><td>Again<td><input type=password name=passa></td></tr>
	<tr><td></td>
EOF
if test -z "$chpass"; then
	echo '<td><input type="submit" name="submit" value="Submit">'
else
	echo '<td><input type="submit" name="chpass" value="ChangePass">'
fi	
cat<<-EOF
	<input type="submit" name="cancel" value="Cancel"></td></tr>
	</table></fieldset></form></body></html>
EOF
