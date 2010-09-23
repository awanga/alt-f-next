
# sed removes any ' that would upset quoted assignment
# awk ensures that 
#	- all variables passed have legal names
#	- special characters are not interpreted by sh
read_args() {
	read -r args
	eval $(echo -n $args | tr '\r' '\n' | sed -e 's/'"'"'/%27/g' | \
		awk 'BEGIN{RS="&";FS="="}
			$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')

	# some forms needs key=value evaluated as value=key,
	# so reverse and evaluate them
	eval $(echo -n $args |  sed -e 's/'"'"'/%27/g' | \
		awk 'BEGIN{RS="&";FS="="}
			$2~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$2,39,$1,39}' )                
}

# return n+1 argument. If called as "lsh 2 one two three" returns "two"
lsh () {
	shift $1
	echo $1
}

checkip() {
#	echo "$1" | grep -q -e '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'
	echo $* | awk '{ nf = split($0, a, ".")
		if (nf < 4) exit 1
		for (i=1; i<=nf; i++) {
			if (a[i] < 0 || a[i] > 255) exit 1
		}
		exit 0
	}'
}

checkmac() {
	echo "$1" | grep -q -e '^\([a-fA-F0-9]\{2\}:\)\{5\}[a-fA-F0-9]\{2\}$'
}

checkname() {
	echo "$1" | grep -v -q -e '^[^a-zA-Z]' -e '[^a-zA-Z0-9-].*'
}

eatspaces() {
	echo "$*" | tr -d ' \t'
}

html_header() {
	echo -e "Content-Type: text/html; charset=UTF-8\n\n<html><body>"
}

debug() {
	echo -e "Content-Type: text/html; charset=UTF-8\n\n<html><body><pre>$(set)</pre>"
}

enddebug() {
	echo "</body></html>"
}

msg() {
	txt=$(echo "$1" | awk '{printf "%s\\n", $0}')

	html_header
	echo "<script type=text/javascript>
	alert(\"$txt\")
//	window.history.back()
	window.location.assign(document.referrer)
	</script>
	</body></html>"
	exit 1
}

has_disks() {
	disks=$(ls /dev/sd?) >/dev/null 2>&1
	ndisks=$(echo "$disks" | grep /dev/ | wc -l)
	if test -z "$disks"; then
		echo "<br><strong>No disks found!</strong><br>"
		echo "</body></html>"
		exit 1
	fi
}

# $1=part (sda2, eg)
isdirty() {
	res="$(tune2fs -l /dev/$1 2> /dev/null)"
	if test $? != 0; then return 1; fi
	if test $(echo "$res" | awk '
		/Filesystem state:/ {print $3}') = "clean"; then
		return 1
	fi
	return 0
}

# $1=part (sda2, eg)
ismount() {
	grep -q ^/dev/$1 /proc/mounts
}

back_button() {
	echo "<input type=button value=\"Back\" onclick=\"history.back()\">"
}

select_part() {
	echo "<select name=part>"
	echo "<option value=none>Select a partition</option>"

	df -h | while read ln; do

	part=""
	eval $(echo $ln | awk '/^\/dev\/(sd|md)/{printf "part=%s; pcap=%s; avai=%s", \
		$1, $2, $4}')
	if test -z $part; then continue; fi
	part=$(basename $part)
	partl=$(plabel $part)
	if test -z "$partl"; then partl=$part; fi

	echo "<option value=$part> $partl ($part, ${pcap}B, ${avai}B free)</option>"
	done
	echo "</select>"
}

firstboot() {
	local curr next
	curr=$(cat /tmp/firstboot 2> /dev/null)
	case "$curr" in
		host) next=time ;;
		time) next=diskwiz ;;
		diskwiz) next=newuser ;;
		newuser) next=settings ;;
		*) ;;
	esac
}

gotopage() {
	cat<<-EOF
		HTTP/1.1 303
		Content-Type: text/html; charset=UTF-8
		Location: $1
	
	EOF
	exit 0
}

check_cookie() {
	eval $HTTP_COOKIE >& /dev/null
	if test "$(cat /tmp/cookie 2> /dev/null)" = "${ALTFID}"; then
		return
	fi
	gotopage /cgi-bin/login.cgi?$REQUEST_URI
}


# usage:
# hlp_msg="This is help"
# <input ... $(help "$hlp_msg")>
help() {
	echo "onmouseover=\"start_pop('$*')\" onmouseout=\"end_pop()\""
}

help_setup() {
	cat<<-EOF
		<script type=text/javascript>
		var wind = null
		var smsg
		var ev = null
		var tid = null
		function end_pop() {
			if (wind != null) {
				wind.close()
				wind = null
			}
			if (tid != null) {
				clearTimeout(tid)
				tid = null
			}
		}
		function start_pop(msg) {
			ev=this.event
			smsg = msg
			end_pop
			tid = setTimeout("help_pop()", 1000);
		}
		function help_pop() {
			if (ev == undefined) {
				x = 100
				y = 100
			} else {
				x = ev.screenX
				y = ev.screenY
			}
			wind = window.open("","","screenX="+x+",screenY="+y+",status=no,location=no,titlebar=no,menubar=no,width=300,height=300")
			wind.document.write("<head><title>Message window</title></head>")
			wind.document.write("<center><big><b>" + smsg + "</b></big></center>")
		}
		</script>
	EOF
}

menu_setup() {
cat<<EOF
<script type="text/javascript">
	function MenuShow() {
		var menu = document.getElementById(this["m_id"])
		var smenu = document.getElementById(this["sm_id"])

		var top  = menu.offsetHeight
		var left = 0

		while(menu) {
			top += menu.offsetTop
			left += menu.offsetLeft
			menu = menu.offsetParent
		}
		smenu.style.position = "absolute"
		smenu.style.top = top + 'px'
		smenu.style.left = left + 'px'
		smenu.style.visibility = "visible"
	}
	function MenuHide() {
		var smenu = document.getElementById(this["sm_id"])
		smenu.style.visibility = "hidden"
	}
	function MenuEntry(menu_id) {
		var menu = document.getElementById(menu_id)
		var smenu = document.getElementById(menu_id + "_sub")

		menu["m_id"] = menu.id
		menu["sm_id"] = smenu.id
		menu.onmouseover = MenuShow
		menu.onmouseout = MenuHide

		smenu["m_id"] = menu.id 
		smenu["sm_id"] = smenu.id
		smenu.style.position = "absolute"
		smenu.style.visibility = "hidden"
		smenu.onmouseover = MenuShow
		smenu.onmouseout = MenuHide
	}
</script>

<style type="text/css">
	a.Menu, div.Menu {
		display: block;
		width: 100px;
		padding: 2px 5px;
		background: #8F8F8F;		
		color: #F0F0F0;
		text-align: center;
		font-family: Sans-Sherif;
		font-size: 0.9em;
		font-weight: 900;
		text-decoration: none;
	}	
</style>
EOF
}

menu_setup2() {
cat<<EOF

<table><tr>
	<td><a class="Menu" href="/cgi-bin/logout.cgi" target="content">Logout</a></td>
	<td><a class="Menu" href="/cgi-bin/status.cgi" target="content">Status</a></div></td>
	<td><div id="Setup" class="Menu">Setup</div></td>
	<td><div id="Disk" class="Menu">Disk</div></td>
	<td><div id="Services" class="Menu">Services</div></td>
	<td><div id="Packages" class="Menu">Packages</div></td>
	<td><div id="System" class="Menu">System</div></td>
</tr></table>

<div id="Setup_sub">
	<a class="Menu" href="/cgi-bin/host.cgi" target="content">Host</a>
	<a class="Menu" href="/cgi-bin/time.cgi" target="content">Time</a>
	<a class="Menu" href="/cgi-bin/mail.cgi" target="content">Mail</a>
	<a class="Menu" href="/cgi-bin/proxy.cgi" target="content">Proxy</a>
	<a class="Menu" href="/cgi-bin/usersgroups.cgi" target="content">Users</a>
</div>
<script type="text/javascript">
	MenuEntry("Setup");
</script>

<div id="Disk_sub">
	<a class="Menu" href="/cgi-bin/diskutil.cgi" target="content">Utilities</a>	
	<a class="Menu" href="/cgi-bin/diskpart.cgi" target="content">Partition</a>
	<a class="Menu" href="/cgi-bin/diskmaint.cgi" target="content">Maintenance</a>
	<a class="Menu" href="/cgi-bin/diskwiz.cgi" target="content">Wizard</a>
</div>
<script type="text/javascript">
	MenuEntry("Disk");
</script>

<div id="Services_sub">
	<a class="Menu" href="/cgi-bin/net_services.cgi" target="content">Network</a>
	<a class="Menu" href="/cgi-bin/sys_services.cgi" target="content">System</a>
	<a class="Menu" href="/cgi-bin/user_services.cgi" target="content">User</a>
</div>
<script type="text/javascript">
	MenuEntry("Services");
</script>

<div id="Packages_sub">
	<a class="Menu" href="/cgi-bin/packages_ipkg.cgi" target="content">Alt-F</a>
	<a class="Menu" href="/cgi-bin/packages_ffp.cgi" target="content">ffp</a>
</div>
<script type="text/javascript">
	MenuEntry("Packages");
</script>

<div id="System_sub">
	<a class="Menu" href="/cgi-bin/sys_utils.cgi" target="content">Utilities</a>
	<a class="Menu" href="/cgi-bin/settings.cgi" target="content">Settings</a>
	<a class="Menu" href="/cgi-bin/firmware.cgi" target="content">Firmware</a>
</div>
<script type="text/javascript">
	MenuEntry("System");
</script>
		
EOF
}

# args: title [refresh time] [onload action]
write_header() {
	cat<<-EOF
		Content-Type: text/html; charset=UTF-8

		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html><head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	EOF

	if ! loadsave_settings -st >/dev/null; then
		warn="<center><h5><font color=red>When done you should save settings</font></h5></center>"
	fi

	if test "$#" = 2 -o \( $# = 3 -a -n "$2" \); then
		echo "<meta http-equiv=\"refresh\" content=\"$2\">"
	fi
	if test "$#" = 3; then
		act="onLoad=\"$3\""
	fi

	cat<<-EOF
		<title>$1</title>
		$(menu_setup)
		</head><body $act>
		$(menu_setup2)
		<!--$(help_setup)-->
		<center><h2>$1</h2></center>
		$warn
	EOF
}

