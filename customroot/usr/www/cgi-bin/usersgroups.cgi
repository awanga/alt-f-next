#!/bin/sh

. common.sh
check_cookie

LOCAL_STYLE='
.fill { width: 100%; }
.almostfill {width: 95%; }
.halffill { float: left; width: 50%; }
.center { clear:both; margin-left:auto; margin-right:auto; width:50%;}
'

write_header "Users and Groups Setup"

has_disks

CONFP=/etc/passwd
CONFG=/etc/group

if ! test -h /home -a -d "$(readlink -f /home)"; then
	cat<<-EOF
		<h4>No users folder found, create it in:</h4>
		<form action="/cgi-bin/newuser_proc.cgi" method=post>
	EOF
	# FIXME offer possibility of creation of Public folders
	select_part
	echo "</select><input type=submit name=create_dir value=CreateDir>
		</form></body></html>"
	exit 0
fi

if ! test -f /usr/bin/quota; then
	quota_dis="disabled"
fi

IFS=":" # WARNING: for all the script
#account:password:UID:GID:GECOS:directory:shell
ucnt=0; ujstr=""
usel='<tr><td colspan=2><select class="fill" size="8" name="users" onChange="update_users()">'
while read user upass uid ugid uname dir shell;do
	if test "${user:0:1}" = "#" -o -z "$user" -o -z "$uid" -o -z "$uname"; then continue; fi
	if test $shell = "/bin/false"; then continue; fi
	if test $uid -lt 100; then continue; fi
	usel="$usel <option>$uname</option>"
	ujstr="$ujstr; users[$ucnt]=\"$user\"; groupsInUser[$ucnt]=\"$(id -Gn $user)\";"
	ucnt=$((ucnt+1))
done < $CONFP
usel="$usel </select></td></tr>"

#group_name:passwd:GID:user_list
gcnt=0; gjstr=""
gsel='<tr><td colspan=2><select class="fill" size="8" name="groups" onChange="update_groups()">'
while read group gpass ggid userl; do
	if test "${group:0:1}" = "#" -o "$gpass" = "!" -o -z "$group"; then continue; fi
	if test $ggid -lt 100 -a $ggid != 80; then continue; fi
	gsel="$gsel <option>$group</option>"

	# primary group
	ul=$(awk -F: '{if ($4 == '$ggid' && substr($0, 1, 1) != "#") printf "%s," $1}' $CONFP)

	# plus suplementary groups, remove dups
	ul=$(echo -e "$userl,$ul" | tr ',' '\n' | sort -u | tr '\n' ':')

	un="" # get user name
	for i in $ul; do 
		un="$(awk -F: '/^'$i':/{printf "%s, ", $5}' $CONFP)${un}"
	done

	gjstr="$gjstr; groups[$gcnt]=\"$group\"; usersInGroup[$gcnt]=\"$un\";"
	gcnt=$((gcnt+1))
done < $CONFG
gsel="$gsel </select></td></tr>"

cat <<EOF
	<script type="text/javascript">
	var users = new Array();
	var groups = new Array();
	var groupsInUser = new Array();
	var usersInGroup = new Array();
	$ujstr
	$gjstr
	function update_users() {
		document.frm.uname.value = document.frm.users.value;
		document.frm.nick.value = users[document.frm.users.selectedIndex];
		document.frm.groupsInUser.value = groupsInUser[document.frm.users.selectedIndex]
	}
	function update_groups() {
		document.frm.gname.value = groups[document.frm.groups.selectedIndex];
		document.frm.usersInGroup.value = usersInGroup[document.frm.groups.selectedIndex]
	}
	function check_group() {
		if (document.frm.gname.value == "") {
			alert("You must fill in the group name or select one group first.")
			return false
		}
		return true
	}
	function check_user() {
		if (document.frm.uname.value == "") {
			alert("You must fill in the user name or select one user first.")
			return false
		}
		return true
	}
	function check_usergroup() {
		if (check_user() && check_group())
			return true
		else
			return false
	}
	</script>
	<form name=frm action="/cgi-bin/usersgroups_proc.cgi" method="post">

	<div class="fill">

	<div class="halffill">
	<fieldset><legend>Users</legend>
	<table class="fill">
	$usel

	<tr><td>User name</td><td><input class="almostfill" type=text size=12 name=uname></td></tr>
	<tr><td>Groups this user belongs to:</td>
		<td><textarea class="almostfill" rows=2 cols=20 name="groupsInUser" readonly></textarea></td></tr>
	<tr><td colspan=2><input type=submit name=new_user value="New">
		<input type=submit name=change_pass value="Password" onclick="return check_user()">
		<input $quota_dis type=submit name=user_quota value="Quota" onclick="return check_user()">
		<input type=submit name=del_user value="Delete" onclick="return check_user()"></td>
	</tr></table></fieldset>

	</div><div class="halffill">
	<fieldset><legend>Groups</legend>
	<table class="fill">
	$gsel

	<tr><td>Group name</td><td><input class="almostfill" type=text size=12 name=gname></td></tr>
	<tr><td>Users belonging to this group:</td>
		<td><textarea class="almostfill" rows=2 cols=20 name="usersInGroup" readonly></textarea></td></tr>
	<tr><td colspan=2><input type=submit name=new_group value="New" onclick="return check_group()">
		<input $quota_dis type=submit name=grp_quota value="Quota" onclick="return check_group()">
	    <input type=submit name=del_group value="Delete" onclick="return check_group()"></td></tr>
	</table></fieldset>
	</div></div>

	<div class="center">
	<fieldset><legend>Users and Groups</legend><table class="fill">
		<tr><td>Add selected user to selected group</td>
			<td><input type=submit name=addToGroup value=Add onclick="return check_usergroup()"></td></tr>
		<tr><td>Remove selected user from selected group</td>
			<td><input type=submit name=delFromGroup value=Delete onclick="return check_usergroup()"></td></tr>
	</table></fieldset>
	</div>
	<input type=hidden name=nick>
	</form></body></html>
EOF
