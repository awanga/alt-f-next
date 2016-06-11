#!/bin/sh

. common.sh
check_cookie

LOCAL_STYLE=".tb_on { 
	background: #ccc;
    border-top: solid 2px #777;
    border-left: solid 2px #777;
    border-bottom:solid 2px  #eaeaea;
    border-right: solid 2px #eaeaea;
}

.tb_off {
	background: #bbb; 
    border-top: solid 2px #eaeaea;
    border-left: solid 2px #eaeaea;
    border-bottom: solid 2px #777;
    border-right: solid 2px #777;
}"

write_header "User script Setup"

cat<<-EOF
	<script language="javascript">
	function togglebutton(el) {
		targ = document.getElementById("edit_id")
		if(el.className == "tb_on") {
			el.className="tb_off";
			targ.style.visibility = "hidden";
			targ.style.display = "none";
		} else {
			el.className="tb_on";
			targ.style.visibility = "visible";
			targ.style.display = "block";
		}
	}
	function msubmit() {
		if (document.getElementById("script_id").value == "" &&
			document.getElementById("tb_id").className == "tb_on") {
			alert("You have to input the full pathname of the script");
			return false;
		}
		return true;
	}
	</script>
EOF

mktt uscript_tt "The full path name of a script to execute at boot time,<br>
such as /mnt/sda2/bootscript.sh or /mnt/md0/bootscript.sh"

defscript='#!/bin/sh

# Script to execute as the root user at boot time.
# You can loose your data or make the system inaccessible
# if using the wrong commands. You have been warned!
 
exec >> /var/log/user.log 2>&1

case "$1" in
	start)
		echo "Starting $0"
		;;
	stop)
		echo "Stopping $0"
		;;
esac
'

CONF_MISC=/etc/misc.conf

if test -s "$CONF_MISC"; then
	. "$CONF_MISC"
fi

us=$(sed -n 's/USER_SCRIPT="\(.*\)"/\1/p' $CONF_MISC)
if test -f "$us"; then
	us=$(readlink -f "$us")
	ufs=$(basename $(dirname $us))
	eus=$(httpd -e "$us")
fi

if test -s "$us"; then
	defscript=$(cat $us)
fi

if ! test "$USER_LOGFILE" = "no"; then
	log_chk="checked"
fi

cat<<-EOF
	<form id=user name=userf action=user_proc.cgi method="post">
	<table><tr>
	<td>Script to execute on powerup:</td>
	<td><input type=text id="script_id" name=user_script value="$eus" $(ttip uscript_tt)></td>
	<td><input type="button" class="tboff" name="edit" id="tb_id" value="Edit" onclick="togglebutton(this)"></td>
	</tr>
	<tr><td>Create diagnostics file:</td>
	<td><input type=checkbox $log_chk name=create_log value="yes"></td></tr>
	</table>
	<textarea id="edit_id" style="visibility:hidden;display:none" rows="15" cols="70" name="userscript">$defscript</textarea>
	<p><input type=submit name=submit value="Submit" onclick="return msubmit()">$(back_button)
	</form></body></html>
EOF

