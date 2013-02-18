
# sed removes any ' or " that would upset quoted assignment
# awk ensures that 
#	- all variables passed have legal names
#	- special characters are not interpreted by sh
read_args() {
	read -r args
	eval $(echo -n $args | tr '\r' '\n' | sed -e 's/'"'"'/%27/g;s/"/%22/g' | \
		awk 'BEGIN{RS="&";FS="="}
			$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')

	# some forms needs key=value evaluated as value=key,
	# so reverse and evaluate them
	eval $(echo -n $args |  sed -e 's/'"'"'/%27/g;s/"/%22/g' | \
		awk 'BEGIN{RS="&";FS="="}
			$2~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$2,39,$1,39}' )                
}

# like read_args above but for QUERY_STRING (does not evaluate value=key)
# split tok[&tok]*, where tok has form "<key=value>"
# notice that QUERY_STRING does not has spaces at its end (busybox httpd bug?)
parse_qstring() {
	eval $(echo -n $QUERY_STRING | sed -e 's/'"'"'/%27/g;s/"/%22/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,substr($0,index($0,$2)),39}')
}

isnumber() {
	echo "$1" | grep -qE '^[0-9.]+$'
}

# Celsius to Fahrenheit 
celtofar() {
	awk 'END{ print 9 * '$1' / 5 + 32}' </dev/null
}

# Fahrenheit to Celsius
fartocel() {
	awk 'END{ printf "%.1f", 5 / 9 * ( '$1' - 32)}' </dev/null
}

checkpass() {
	lpass=$(httpd -d "$1")
	if test -n "$lpass"; then
		if test -n "$(echo \"$lpass\" | tr -d [!-~])"; then
			echo "Use only ASCII characters and no spaces for the password: allowed are\n\
letters, numbers and ! \\\" # $ % & \' ( ) * + , - . / : ; < = > ? @ [ \\\ ] ^ _ \` { | } ~"
			return 1
		else
			echo $lpass
			return 0
		fi
	else
		echo "Password can't be empty"
		return 1
	fi
}

checkip() {
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

checkport() {
	if netstat -ltn 2> /dev/null | grep -q ":$1 "; then return 0; fi
	return 1
}

checkname() {
	echo "$1" | grep -v -q -e '^[^a-zA-Z]' -e '[^a-zA-Z0-9-].*'
}


find_mp() {
	if ! test -d "$1"; then return 1; fi
	tmp=$(readlink -f "$1")
	while ! mountpoint -q "$tmp"; do
		tmp=$(dirname "$tmp")
	done
	echo $tmp
}

check_folder() {
	if ! tmp=$(find_mp "$1"); then
		echo "\"$1\" does not exists or is not a folder."
		return 1
	fi

	if test "$tmp" = "/" -o "$tmp" = "."; then
		echo "\"$1\" is not on a filesystem."
		return 1
	fi

	if test "$tmp" = "$1"; then
		echo "\"$1\" is a filesystem root, not a folder."
		return 1
	fi
}

eatspaces() {
	echo "$*" | tr -d ' \t'
}

# mainly for fstab usage, where spaces are '\040' coded
path_escape() {
	echo "$1" | sed 's/ /\\040/g'
}

path_unescape() {
	echo "$1" | sed 's/\\040/ /g'
}

# for http only <>&"' needs to be encoded, but possible clash with some linux utilities
# quoting and special chars meaning and javascript quoting advises doing it
# characters in the hexadecimal ranges 0-08, 0B-0C, 0E-1F, 7F, and 80-9F cannot be used in HTML
# Wouldn't be faster doing it as in url_encode() bellow?
#
# in the bellow httpencode() the following is missing
# s/	/\&#x09;/g
# s/!/\&#x21;/g
# s/#/\&#x23;/g
# s/\\$/\&#x24;/g
# s/%/\&#x25;/g
# s/;/&#x3b;/g

http_encode() {
echo "$1" | sed "
s/\&/\&#x26;/g
s/ /\&#x20;/g
s/\"/\&#x22;/g
s/'/\&#x27;/g
s/(/\&#x28;/g
s/)/\&#x29;/g
s/\*/\&#x2a;/g
s/+/\&#x2b;/g
s/,/\&#x2c;/g
s/-/\&#x2d;/g
s/\./\&#x2e;/g
s/\//\&#x2f;/g
s/:/\&#x3a;/g
s/</\&#x3c;/g
s/=/\&#x3d;/g
s/>/\&#x3e;/g
s/?/\&#x3f;/g
s/@/\&#x40;/g
s/\[/\&#x5b;/g
s/\\\/\&#x5c;/g
s/\]/\&#x5d;/g
s/\^/\&#x5e;/g
s/_/\&#x5f;/g
s/\`/\&#x60;/g
s/{/\&#x7b;/g
s/|/\&#x7c;/g
s/}/\&#x7d;/g
s/~/\&#x7e;/g
"
}

# "Characters from the unreserved set never need to be percent-encoded". But is much faster to do.
# Reserved chars: !*'();:@&=+$,/?#[]
#
# FIXME: howto make hexdump to output a '%'?
url_encode() {
	echo -n "$1" | hexdump -ve '/1 "-%X"' | tr '-' '%'
}

# deprecated, too slow and does unnecessary UTF-8 encoding (the doctype charset is UTF-8)
httpencode() {
	echo -n "$1" | iconv -s -f UTF-8 -t UCS-2LE | hexdump -ve '/2 "&#%u;"'
}

# deprecated, use url_encode above (but is it faster?)
urlencode() {
echo "$1" | sed " 
s/	/%09/g
s/ /%20/g
s/!/%21/g
s/\"/%22/g
s/#/%23/g
s/\\$/%24/g
s/%/%25/g
s/\&/%26/g
s/'/%27/g
s/(/%28/g
s/)/%29/g
s/\*/%2a/g
s/+/%2b/g
s/,/%2c/g
s/-/%2d/g
s/\./%2e/g
s/\//%2f/g
s/:/%3a/g
s/;/%3b/g
s/</%3c/g
s/=/%3d/g
s/>/%3e/g
s/?/%3f/g
s/@/%40/g
s/\[/%5b/g
s/\\\/%5c/g
s/\]/%5d/g
s/\^/%5e/g
s/_/%5f/g
s/\`/%60/g
s/{/%7b/g
s/|/%7c/g
s/}/%7d/g
s/~/%7e/g
"
}

# $1-title (optional)
html_header() {
	if test -n "$HTML_HEADER_DONE"; then return; fi
	HTML_HEADER_DONE="yes"
	if test "$#" != 0; then
		center="<center><h2>$1</h2></center>"
	fi

	cat<<-EOF
		Content-Type: text/html; charset=UTF-8

		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<style type="text/css">html { height: 100%; }</style><title></title>
		</head><body style="height: 100%; font-family: arial,verdana">
		$center
	EOF
}

debug() {
	HTML_HEADER_DONE="yes"
	echo -e "Content-Type: text/html; charset=UTF-8\n\n<html><body><pre>$(set)</pre>"
}

enddebug() {
	echo "</body></html>"
}

msg() {
	txt=$(echo "$1" | sed 's|"|\\"|g' | awk '{printf "%s\\n", $0}')

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
	flashed_firmware=$(dd if=/dev/mtdblock2 ibs=64 count=1 2> /dev/null | strings)
	echo $flashed_firmware | grep -q Alt-F
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

find_dm() {
	eval $(dmsetup info /dev/$1/$2 | awk '/Major/{printf "mj=%d mi=%d", $3, $4}')
	awk '/'$mj' *'$mi'/{printf "%s", $4}' /proc/partitions
}

# $1=sda global: ln 
fs_progress() {
	part=$1
	ln=""
	for k in check format convert shrink enlarg wip; do
		if test -s /tmp/${k}-${part}; then
			if kill -1 $(cat /tmp/${k}-${part}.pid) 2> /dev/null; then
				if test -s /tmp/${k}-${part}.log; then
					ln=$(cat /tmp/${k}-${part}.log | tr -s '\b\r\001\002' '\n' | tail -n1)
				fi
				if test $k = "check"; then
					ln=$(echo $ln | awk '{if ($3 != 0) printf "step %d: %d%%", $1, $2*100/$3}')
				elif test $k = "format"; then
					ln=$(echo $ln | awk -F/ '/.*\/.*/{if ($2 != 0) printf "%d%%", $1*100/$2}')
				elif test $k = "shrink" -o $k = "enlarg"; then
					ln=$(echo $ln | grep -o X)
					if test -n "$ln"; then
						ln=" step 2: $(expr $(echo "$ln" | wc -l) \* 100 / 40)%"
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

# $1=pre-select part (eg: sda4)
select_part() {
	if test -n "$1"; then presel=$1; fi

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
		sel=""; if test "$presel" = "$part"; then sel="selected"; fi		
		echo "<option $sel value=$part> $partl ($part, ${pcap}B, ${avai}B free${partb})</option>"
	done
	echo "</select>"
}

upload_file() {
	# POST upload format:
	# -----------------------------29995809218093749221856446032^M
	# Content-Disposition: form-data; name="file1"; filename="..."^M
	# Content-Type: application/octet-stream^M
	# ^M    <--------- headers end with empty line
	# file contents
	# file contents
	# file contents
	# ^M    <--------- extra empty line
	# -----------------------------29995809218093749221856446032--^M

	# The form might contain other fields, all are delimited by the initial delimiter
	# the file and other fields might appear mixed.
	# It looks like the order is the one in the form
	# -----------------------------9708682921188161811539875626^M
	# Content-Disposition: form-data; name="xpto1"^M
	# ^M
	# contents
	# ^M
	# -----------------------------9708682921188161811539875626^M

	upfile=$(mktemp -t)
	TF=$(mktemp -t)

	read -r delim_line
	while read -r line; do
		if test "${line%:*}" = "Content-Type"; then
			read -r line
			break
		fi
	done

	cat > $upfile

	# remove from first delimiter found until EOF
	sed -i '/'$delim_line'/,$d' $upfile

	# but miss to remove the cr nl before the delimiter, which is now at EOF
	# pitty "head -c -2" doesn't work
	len=$(expr $(stat -t $upfile | cut -d" " -f2) - 2)
	dd if=$upfile of=$TF bs=$len count=1 >/dev/null 2>&1
	rm -f $upfile
	echo $TF
}

download_file() {
	echo -e "HTTP/1.1 200 OK\r"
	echo -e "Content-Disposition: attachment; filename=\"$(basename $1)\"\r"
	echo -e "Content-Type: application/octet-stream\r"
	echo -e "\r"
	cat $1
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
	html_header
	cat<<-EOF
		<script type="text/javascript">
			window.location.assign("$1")
		</script>
		</body></html>
	EOF
	exit 0
}

check_cookie() {
	eval $HTTP_COOKIE >& /dev/null
	if test -n "$HTTP_COOKIE" -a -f /tmp/cookie; then
		if test $(expr $(date +%s) - $(date +%s -r /tmp/cookie) ) -lt 1800; then
			if test "$(cat /tmp/cookie)" = "${ALTFID}"; then
				touch /tmp/cookie
				return
			fi
		fi
		rm /tmp/cookie
	fi
	html_header
	cat<<-EOF
		<script type="text/javascript">
			parent.frames.content.location.assign("/cgi-bin/login.cgi?$REQUEST_URI")
			parent.frames.nav.location.assign("/cgi-bin/index.cgi")
		</script></body></html>
	EOF
	exit 0
}

busy_cursor_start() {
	html_header
	cat<<-EOF
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
	tmp_id=$(mktemp -t)
	tid=$(basename $tmp_id)
	cat<<-EOF
		$1: <span id="$tid">0</span>
		<script type="text/javascript">
			function wait_count_update(id) {
				obj = document.getElementById(id);
				obj.innerHTML = parseInt(obj.innerHTML) + 1;
			}
			var waittimerID;
			waittimerID = setInterval("wait_count_update('$tid')",1000);
			document.body.style.cursor = 'wait';
		</script>
	EOF
}

wait_count_stop() {
	rm -f $tmp_id
	cat<<-EOF	
		<script type="text/javascript">
			clearInterval(waittimerID);
			document.body.style.cursor = '';
		</script>
	EOF
}

# use an iframe to embed apps own webpages
# FIXME, iframe height!
# $1=url to open, $2=page title
embed_page() {
	write_header ""

	cat<<-EOF
		<form name="embedf" action="zpto" method="post">
		<input type=hidden name="ifsrc" value="$1">
		<input type=hidden name="ifname" value="$2">
		</form>
		<iframe src="$1" width="100%" height="95%" frameborder="0" scrolling="auto"></iframe>
		</body></html>
	EOF
	exit 0
}

# Contributed by Dwight Hubbard, dwight.hubbard <guess> gmail.com
# Adapted by Joao Cardoso
#
# draws a bar graph, $1 is the percentage to display (1-100) and $2 is the text to display,
# if $2 is not present $1 is displayed for the text.  Normally $2 is used when graphing data
# that has a range other than 1-100.
# Note since this graph uses a div it doesn't display inline
drawbargraph() {

	linewidth="$1"
	if test "$linewidth" -gt 100; then
		linewidth="100"
	fi

	if [ "$2" == "" ]; then
		text="$1%"
	else
		text="$2"
	fi

	if test "$linewidth" -gt 90; then
		bgcolor="#F66"
		fgcolor="#FFF"
	elif test "$linewidth" -gt 75; then
		bgcolor="#FF5"
		fgcolor="#000"
	else
		bgcolor="#6F6"
		fgcolor="#000"
	fi

	cat <<-EOF
	<div class="meter-wrap">
		<div class="meter-value" style="background-color: $bgcolor; width: $linewidth%;">
			<div class="meter-text" style="color: $fgcolor;">$text</div>
		</div>
	</div>
	EOF
}

drawbargraph_setup() {
cat<<EOF
	<style type="text/css">
		.meter-wrap {
			position: relative; z-index: -1;
		}
		.meter-wrap, .meter-value, .meter-text {
			width: 100px; height: 1em;
		}	
		.meter-wrap, .meter-value {
			background: #bdbdbd top left no-repeat;
		}		   
		.meter-text {
			position: absolute;
			top:0; left:0;
			text-align: center;
			width: 100%;
			font-size: .8em;
		}
	</style>
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
		font-family: arial,verdana;
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

bookmf() {
cat<<EOF
	<script type="text/javascript">
		function commonbookmark() {
			try {
				x = parent.content.document.embedf
				title = x.ifname.value
				url = x.ifsrc.value
			} catch(err) {
				title = parent.content.document.title
				url = parent.content.document.location.pathname
			}
			return title + "&url=" + url
		}
		function addbookmark() {			
			parent.content.document.location.assign("/cgi-bin/bookmark.cgi?add=" + commonbookmark())
			return false
		}
		function rmbookmark() {
			parent.content.document.location.assign("/cgi-bin/bookmark.cgi?rm=" + commonbookmark())
			return false
		}
		function rmall() {
			try {
				url = parent.content.document.embedf.ifsrc.value
			} catch(err) {
				url = parent.content.document.location.pathname
			}
			parent.content.document.location.assign("/cgi-bin/bookmark.cgi?rm=all&url=" + url)
			return false
		}
	</script>
EOF
}

menu_setup() {
cat<<EOF
	<script type="text/javascript">
	top.document.title = "($(hostname)) Alt-F " + document.title;
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
	html { height:95%; }

	a.Menu, div.Menu {
		display: block;
		width: 100px;
		padding: 2px 5px;
		background: #8F8F8F;		
		color: #F0F0F0;
		text-align: center;
		font-family: arial,verdana;
		font-size: 0.9em;
		font-weight: 900;
		text-decoration: none;
	}	
	</style>
EOF
}

fill_menu() {
	echo "<td><div id=\"$1\" class=\"Menu\">$1</div><div id=\"$1_sub\">"
	extra=$(cat $1*.men)
	IFS=" "
	echo $extra | while read entry url; do
		echo "<a class=\"Menu\" href=\"/cgi-bin/$url\" target=\"content\">$entry</a>"
	done
	echo "</div><script type=\"text/javascript\">MenuEntry(\"$1\");</script></td>"
}

bookmark_fill() {
cat<<EOF
	<td><div id="Bookmark" class="Menu">Bookmark</div><div id="Bookmark_sub">
	<a class="Menu" href="" onclick="return addbookmark()">Add</a>
	<a class="Menu" href="" onclick="return rmbookmark()">Remove</a>
	<a class="Menu" href="" onclick="return rmall()">Remove All</a>
	</div><script type="text/javascript">MenuEntry("Bookmark")</script>
	</td></tr></table>
EOF
}

# $1-page title $2-script
menu_setup2() {
cat<<EOF
	<table cellspacing=0><tr>
		<td><a class="Menu" href="/cgi-bin/logout.cgi" target="content">Logout</a></td>
		<td><a class="Menu" href="/cgi-bin/status.cgi" target="content">Status</a></td>
EOF

	for i in Setup Disk Services Packages System; do
		fill_menu $i
	done
	bookmark_fill
}

# args: title [onload action]
write_header() {
	HTML_HEADER_DONE="yes"
	cat<<-EOF
		Content-Type: text/html; charset=UTF-8

		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html><head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	EOF

	if ! loadsave_settings -st >/dev/null; then
		warn_tt="The following files have changed since the last save:<br>$(loadsave_settings -lc | sed -n 's/ /<br>/gp')"
		warn="<center><h5>
			<a href=\"/cgi-bin/settings.cgi\" $(ttip tt_settings)
			style=\"text-decoration: none; color: red\">
			When done you must <u>save settings</u>
			<img src=\"../help.png\" width=11 height=11 alt=\"help\" border=0>
			</a></h5></center>"
	fi

	if test "$#" = 2; then
		act="onLoad=\"$2\""
	fi

	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		hlp="<a href=\"../$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi
	
	cat<<-EOF
		<title>$1</title>
		$(menu_setup)
		$(tooltip_setup)
		$(drawbargraph_setup)
		$(bookmf)
		</head>
		<body style="height: 95%; font-family: arial,verdana" $act>
		$(menu_setup2 "$1" "/cgi-bin/$0") 
		$(mktt tt_help "Get a descriptive help")
		$(mktt tt_settings "$warn_tt")
		<center><h2>$1 $hlp</h2></center>
		$warn
	EOF
}
