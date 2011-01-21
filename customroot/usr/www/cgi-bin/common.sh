
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

isnumber() {
	echo "$1" | grep -qE '^[0-9]+$'
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

path_escape() {
	echo $(echo "$1" | sed 's/ /\\040/g')
}

path_unescape() {
	echo $(echo "$1" | sed 's/\\040/ /g')
}

# $1-share "[Public (Read Write)]"
make_available() {

	share="$1"

	awk '{
		while ($0 != "'"$share"'") { print $0; if (! getline) exit }
		print $0; getline
		while ($1 != "available" && substr($0,1,1) != "[") { print $0; 	getline	}
		if ($1 == "available") print "available = yes"
		else print $0
		while(getline) print $0
	}' /etc/samba/smb.conf > /etc/samba/smb.conf-new

#	mv /etc/samba/smb.conf /etc/samba/smb.conf-
	mv /etc/samba/smb.conf-new /etc/samba/smb.conf
	if rcsmb status >& /dev/null; then
		rcsmb reload >& /dev/null
	fi
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

# $1=sda
disk_details() {
	. /etc/bay
	dbay=$(eval echo \$$1)
	dcap="$(eval echo \$${dbay}_cap)"
	dfam="$(eval echo \$${dbay}_fam)"
	dmod="$(eval echo \$${dbay}_mod)"
	if echo $dbay | grep -q ^usb; then
		dbay=${dbay:0:3}
	fi
}

# $1=sda
disk_power() {
	if test -b /dev/$1; then
		echo $(hdparm -C /dev/$1 2> /dev/null | awk '/drive/{print $4}')
	else
		echo "None"
	fi
}

# returns true if Alt-F is flashed
isflashed() {
	TF=$(mktemp -t)
	dd if=/dev/mtdblock2 of=$TF count=1 >& /dev/null
	strings $TF | grep -q Alt-F
#	strings $TF | grep -q xpto
	st=$?
	rm $TF
	return $st
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

# $1=sda global: ln 
fs_progress() {
	part=$1
	ln=""
	for k in clean format convert shrink enlarg wip; do
		if test -f /tmp/${k}-${part}; then
			if kill -1 $(cat /tmp/${k}-${part}.pid) 2> /dev/null; then
				if test -f /tmp/${k}-${part}.log; then
					ln=$(cat /tmp/${k}-${part}.log | tr -s '\b\r\001\002' '\n' | tail -n1)
				fi
				if test $k != "wip"; then
					ln=$(echo $ln | grep -oE ' [0-9]+.[0-9]+%|X|[0-9]+/[0-9]+')
					if echo $ln | grep -q X; then
						ln=" step 2: $(expr $(echo "$ln" | wc -l) \* 100 / 40)%"
					elif echo $ln | grep -q '[0-9]+/[0-9]+/'; then
						ln="$(expr $(echo $ln | cut -d"/" -f1) \* 100 / $(echo $ln | cut -d"/" -f2))%"
					fi 
				fi
				ln="${k}ing...$ln"
			else
				rm /tmp/${k}-${part}*
			fi
		fi
	done
}

back_button() {
	echo "<input type=button value=\"Back\" onclick=\"history.back()\">"
}

select_part() {
	echo "<select name=part>"
	echo "<option value=none>Select a filesystem</option>"

	df -h | while read ln; do
		part=""
		eval $(echo $ln | awk '/^\/dev\/(sd|md)/{printf "part=%s; pcap=%s; avai=%s", \
			$1, $2, $4}')
		if test -z $part; then continue; fi
		part=$(basename $part)
		partl=$(plabel $part)
		partb=$(sed -n "s/${part%[0-9]}=\(.*\)/, \1 disk/p" /etc/bay)
		if test -z "$partl"; then partl=$part; fi

		echo "<option value=$part> $partl ($part, ${pcap}B, ${avai}B free${partb})</option>"
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

js_gotopage() {
	cat<<-EOF
		<script type="text/javascript">
			window.location.assign("http://" + location.hostname + "$1")
		</script>
	EOF
}

check_cookie() {
	eval $HTTP_COOKIE >& /dev/null
	if test -n "$HTTP_COOKIE" -a -f /tmp/cookie; then
		if test "$(cat /tmp/cookie)" = "${ALTFID}"; then
			return
		fi
	fi
	gotopage /cgi-bin/login.cgi?$REQUEST_URI
}

busy_cursor_start() {
	cat<<-EOF
		<style>	body { height : 100%;} </style>
		<script type="text/javascript">
			document.body.style.cursor = 'wait';
		</script>
	EOF
}

busy_cursor_end() {
	cat<<-EOF
		<script type="text/javascript">
			document.body.style.cursor = '';
		</script>
	EOF
}

# wait_count $1=msg
wait_count_start() {
	tmp_id=$(mktemp)
	cat<<-EOF
		$1: <span id="$tmp_id">0</span>
		<style>	body { height : 100%;} </style>
		<script type="text/javascript">
			function wait_count_update(id) {
				obj = document.getElementById(id);
				obj.innerHTML = parseInt(obj.innerHTML) + 1;
			}
			var waittimerID;
			waittimerID = setInterval("wait_count_update('$tmp_id')",1000);
			document.body.style.cursor = 'wait';
		</script>
	EOF
}

wait_count_stop() {
	rm $tmp_id
	cat<<-EOF	
		<script type="text/javascript">
			clearInterval(waittimerID);
			document.body.style.cursor = '';
		</script>
	EOF
}

# usage: mktt tt_id "tooltip msg" 
mktt () {
	echo "<div id=\"$1\" class=\"ttip\">$2</div>"
}

# usage:
# mktt tt_id "tooltip message"
# <input ... $(ttip tt_id)>
ttip() {
	echo "onmouseover=\"popUp(event,'$1')\" onmouseout=\"popDown('$1')\""
}

tooltip_setup() {
cat<<EOF
	<script type="text/javascript">

	var stat_id
	var stat_ev

	function popDown(id) {
		if (stat_id)
			clearTimeout(stat_id);
		stat_id = null;
		document.getElementById(id).style.visibility = "hidden";
	}

	function popUp(ev, id) {
		if (stat_id)
			clearTimeout(stat_id);
		stat_ev = ev;
		stat_id = id;
		setTimeout("iPopUp()", 1000)
	}

	function iPopUp() {
		if (! stat_id)
			return;

		obj = document.getElementById(stat_id);
		stat_id = null

		objWidth = obj.offsetWidth;
		objHeight = obj.offsetHeight;

		y = stat_ev.pageY + 20;
		x = stat_ev.pageX - objWidth/4;

		if (x + objWidth > window.innerWidth)
			x -= objWidth/2;
		else if (x < 2)
			x = 2;

		if (y + objHeight > window.innerHeight)
			y -= 2*objHeight;

		obj.style.left = x + 'px';
		obj.style.top = y + 'px';
		obj.style.visibility = "visible";
	}
	</script>

	<style type="text/css">
	.ttip {
		font-family: sans-serif;
		border: solid 1px black;
		padding: 2px;

		color: #333333;
		background-color: #ffffaa;

		position: absolute;
		visibility: hidden;
	}
	</style>
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
		<a class="Menu" href="/cgi-bin/hosts.cgi" target="content">Hosts</a>
		<a class="Menu" href="/cgi-bin/usersgroups.cgi" target="content">Users</a>
		<a class="Menu" href="/cgi-bin/browse_dir.cgi?wind=no?browse=/mnt" target="content">Directories</a>
	</div>
	<script type="text/javascript">
		MenuEntry("Setup");
	</script>

	<div id="Disk_sub">
		<a class="Menu" href="/cgi-bin/diskutil.cgi" target="content">Utilities</a>	
		<a class="Menu" href="/cgi-bin/diskmaint.cgi" target="content">Filesystems</a>
		<a class="Menu" href="/cgi-bin/raid.cgi" target="content">RAID</a>
		<a class="Menu" href="/cgi-bin/diskpart.cgi" target="content">Partitioner</a>
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

# args: title [onload action]
write_header() {
	cat<<-EOF
		Content-Type: text/html; charset=UTF-8

		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html><head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	EOF

	if ! loadsave_settings -st >/dev/null; then
		warn_tt="The following files have changed since the last save:<br>$(loadsave_settings -lc | sed -n 's/ /<br>/gp')"
		warn="<center><h5>
			<a href=\"javascript:void(0)\" $(ttip tt_settings)
			style=\"text-decoration: none; color: red\">
			When done you should save settings
			<img src=\"../help.png\" width=11 height=11 alt=\"help\" border=0>
			</a></h5></center>"
	fi

	if test "$#" = 2; then
		act="onLoad=\"$2\""
	fi

	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		hlp="<a href=\"http://$HTTP_HOST/$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi
	
	cat<<-EOF
		<title>$1</title>
		$(menu_setup)
		$(tooltip_setup)
		</head>
		<body $act>
		$(menu_setup2)
		$(mktt tt_help "Get a descriptive help")
		$(mktt tt_settings "$warn_tt")
		<center><h2>$1 $hlp</h2></center>
		$warn
	EOF
}
