
CONF_MISC=/etc/misc.conf

# sed removes any ' or " that would upset quoted assignment
# awk ensures that 
# - all variables passed have legal names
# - special characters are not interpreted by sh
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
	awk 'END{ printf "%d", 9 * '$1' / 5 + 32}' </dev/null
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
letters, numbers and ! \" # $ % & \' ( ) * + , - . / : ; < = > ? @ [ \\\ ] ^ _ \` { | } ~"
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

check_https() {
	if echo $HTTP_REFERER | grep -q 'http://'; then
		echo "<h4 class=\"warn\">You are using plain http, password will be transmited in clear.<br>
	You should use instead a <a href=\"https://${HTTP_HOST%%:*}\" target=\"_top\">secure https connection</a>.<br>$1</h4>"
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
	netstat -ltn 2> /dev/null | grep -q ":$1[[:space:]]"
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

# FIXME: missing
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

# FIXME: howto make hexdump to output a '%'?
url_encode() {
	echo -n "$1" | hexdump -ve '/1 "-%X"' | tr '-' '%'
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
	grep -q ^/dev/$1[[:space:]] /proc/mounts
}

find_dm() {
	eval $(dmsetup info /dev/$1/$2 | awk '/Major/{printf "mj=%d mi=%d", $3, $4}')
	awk '/'$mj' *'$mi'/{printf "%s", $4}' /proc/partitions
}

# $1=sda global: ln 
fs_progress() {
	part=$1
	ln=""
	for k in check fix format convert shrink enlarg wip; do
		if test -f /tmp/${k}-${part}; then
			if kill -0 $(cat /tmp/${k}-${part}.pid) 2> /dev/null; then
				if test -s /tmp/${k}-${part}.log; then
					ln=$(cat /tmp/${k}-${part}.log | tr -s '\b\r\001\002' '\n' | tail -n1)
				fi
				if test $k = "check" -o $k = "fix"; then
					ln=$(echo $ln | awk '{ $3 += 0; if ($3 != 0) printf "step %d: %d%%", $1, $2*100/$3}')
				elif test $k = "format"; then
					#ln=$(echo $ln | awk -F/ '/.*\/.*/{ $2 += 0; if ($2 != 0) printf "%d%%", $1*100/$2}')
					ln=""
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

firstboot() {
	if ! test -f /tmp/firstboot; then return; fi

	pg=${0%.cgi}
	if test "$pg" = "login"; then return; fi

	currst=$(cat /tmp/firstboot)
	currpg=${currst%_?}

	if echo $0 | grep -q '_proc\.cgi'; then
		ppg=${0%_proc.cgi}
	fi

	if test -z "$ppg" -a "$pg" != "$currpg"; then
		gotopage /cgi-bin/${currpg}.cgi
		exit 0
	fi

msg1="Welcome to your first login to Alt-F.<br><br> <em>If you know what you are doing</em>, Logout to skip this wizard.<br><br>"
msg_host="You should now fill-in all the host details and Submit them."
msg_time_1="You should now specify the Continent/City where you live and Submit it.<br>"
msg_time_2="You should now adjust the current date and time, either through the internet or manually, and Submit it."
msg_diskwiz="You should now select a disk configuration."
msg_newuser_1="You should now specify the filesystem where users will login and store their personal data."
msg_newuser_2="You should now create an user account."
msg_smb="You can now create new folders and define them as network shares."
msg_packages_ipkg="You should now specify the filesystem where Alt-F packages can be installed."
msg_settings="You should now save in flash memory the changes that you have just made.<br>
You should do it whenever you want your changes to survive a box reboot."

	case "$currst" in
		host) next=time_1;;
		time_1) next=time_2;;
		time_2) next=diskwiz;; 
		diskwiz) next=newuser_1;;
		newuser_1) next=newuser_2;; 
		newuser_2) next=smb;;
		smb) if grep -q 'DNS-323' /tmp/board; then next=settings; else next=packages_ipkg; fi;;
		packages_ipkg) next=settings;;
		settings) next=status;; 
		*) rm /tmp/firstboot; firstmsg=""; return ;;
	esac

	firstmsg="<h4 class=\"warn\">$msg1 $(eval echo \$msg_$currst)</h4>"

	if test "$ppg" = "$currpg"; then
		echo $next > /tmp/firstboot
	fi
}

# $1-title (optional)
html_header() {
	if test -n "$HTML_HEADER_DONE"; then return; fi
	HTML_HEADER_DONE="yes"
	if test "$#" != 0; then
		center="<h2 class="title">$1</h2>"
	fi

	echo -e "Content-Type: text/html; charset=UTF-8\r\n\r"

	cat<<-EOF
		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html><head profile="http://www.w3.org/2005/10/profile">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<link rel="icon" type="image/png" href="../dns-323.png">
		<style type="text/css">
			$(echo "$LOCAL_STYLE")
			html { height: 100%; }
			body { height: 100%; font-family: arial,verdana; }
		</style>
		$(load_thm default.thm)	
		<title></title></head>
		<body>
		$center
	EOF
}

debug() {
	HTML_HEADER_DONE="yes"
	echo -e "Content-Type: text/html; charset=UTF-8\r\n\r"
	echo "<html><body><pre>$(set)"
}

enddebug() {
	echo "</pre></body></html>"
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

back_button() {
	echo "<input type=button value=\"Back\" onclick=\"history.back()\">"
}

# $1-label $2-url
goto_button() {
	echo "<input type=button value=\"$1\" onclick=\"window.location.assign('$2')\">"
}

# $1=pre-select part (eg: sda4) $2=name postfix, e.g. '1', optional
select_part() {
	if test -n "$1"; then presel=$1; fi

	echo "<select name=part$2>"
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

	eval $(df -m /tmp | awk '/tmpfs/{printf "totalm=%d; freem=%d;", $2, $4}')
	reqm=$((CONTENT_LENGTH * 2 / 1024 / 1024))
	if test "$reqm" -gt "$freem"; then
		if ! mount -o remount,size=$((totalm + reqm + 10 - freem))M /tmp; then
			cat > /dev/null # discard transfer
			echo "Not enought /tmp memory,\n$reqm MB required, $freem MB available.\nIs swap active?"
			return 1
		fi
	fi

	read -r delim_line
	read -r Content_Disposition
	read -r Content_Type
	read -r empty_line

	if ! echo "$CONTENT_TYPE" | grep -q multipart/form-data && 
		echo "$Content_Disposition" | grep -q form-data &&
		echo "$Content_Type" | grep -q 'application/octet-stream'; then
			cat > /dev/null # discard transfer
			echo "Not a (simple) POST response, try another browser?"
			return 1
	fi

if false; then
	# each var has 2 extra bytes (\r\n), and last boundary has two trailing '-'
	fs=$((CONTENT_LENGTH - 2 \* ${#delim_line} - ${#Content_Disposition} - ${#Content_Type} - 10))

	upfile=$(mktemp -t)
	head -c $fs > $upfile

	echo $upfile

else
	fname1=$(echo $Content_Disposition | sed -n 's/.*[[:space:]]name="\(.*\)";.*/\1/p')
	hfname1=$(echo $Content_Disposition | sed -n 's/.*[[:space:]]filename="\(.*\)".*/\1/p')
	if test -z "$hfname1"; then
		cat > /dev/null # discard transfer
		echo "Not a valid Content_Disposition POST response, try another browser?"
		return 1
	fi

	fname1=/tmp/$fname1
	cat > $fname1

	# get next file name
	fname2=$(sed -n '/^Content-Disposition:/s/.*[[:space:]]name="\(.*\)";.*/\1/p' $fname1)
	hfname2=$(sed -n '/^Content-Disposition:/s/.*[[:space:]]filename="\(.*\)".*/\1/p' $fname1)

	if test -n "$hfname2"; then
		fname2=/tmp/$fname2
		sed -n '/'$delim_line'/,$p' $fname1 > $fname2

		# remove delim-line, cont-disp, cont-type, empty line, last empty line
		sed -i '1,4d' $fname2
		sed -i '$d' $fname2
		sed -i '$d' $fname2
	fi

	# remove fname2 from fname1 end (\r\n empty lines)
	sed -i '/'$delim_line'/,$d' $fname1
	#sed -i '$d' $fname1 # buggy busybox sed when last chars are '00 00  ff ff'
	flen=$(stat -t $fname1 | cut -d" " -f2)
	dd if=$fname1 of=$fname1 bs=1 seek=$((flen - 2)) count=0 >& /dev/null
	echo $fname1
fi

}

download_file() {
	echo -e "HTTP/1.1 200 OK\r"
	echo -e "Content-Disposition: attachment; filename=\"$(basename $1)\"\r"
	echo -e "Content-Type: application/octet-stream\r\n\r"
	cat $1
}

# from_url location
gotoback() {
	from_url=$(httpd -d "$1")
	if echo "$from_url" | grep -q index.cgi; then
		gotopage /cgi-bin/$2
	else
		gotopage $from_url
	fi
}

gotopage() {
	if echo $0 | grep -q '_proc\.cgi'; then firstboot; fi
	
	echo -e "HTTP/1.1 303\r"
	echo -e "Content-Type: text/html; charset=UTF-8\r"
	echo -e "Location: $1\r\n\r"

	exit 0
}

js_gotopage() {
	if echo $0 | grep -q '_proc\.cgi'; then firstboot; fi
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
	if test -n "$HTTP_COOKIE" -a -O /tmp/cookie; then
		ALTFID=$(echo $HTTP_COOKIE | sed -n 's/ALTFID=\([^[:space:],;]*\).*/\1/p')   
        if test -n "$ALTFID"; then
			if test $(expr $(date +%s) - $(date +%s -r /tmp/cookie) ) -lt 1800; then
				if test "$(cat /tmp/cookie)" = "${ALTFID}"; then
					touch /tmp/cookie
					return
				else
					logger -t httpd "Unautorized access attempted with cookie \"${ALTFID}\""
				fi
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

# Contributed by Dwight Hubbard, dwight.hubbard <guess> gmail.com, adapted by Joao Cardoso
# draws a bar graph, $1 is the percentage to display (1-100) and $2 is the text to display,
# if $2 is not present $1 is displayed for the text. Normally $2 is used when graphing data
# that has a range other than 1-100. Since this graph uses a div it doesn't display inline
drawbargraph() {

	linewidth="$1"
	if test "$linewidth" -gt 100; then
		linewidth="100"
	fi

	if test "$2" == ""; then text="$1%"; else text="$2"; fi
	if test "$3" == ""; then yellow=80; else yellow=$3; fi
	if test "$4" == ""; then red=90; else red=$4; fi

	if test "$linewidth" -gt $red; then
		bgcolor="#F66"
		fgcolor="#FFF"
	elif test "$linewidth" -gt $yellow; then
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

# usage: mktt tt_id "tooltip msg" 
mktt() {
	echo "<div id=\"$1\" class=\"ttip\">$2</div>"
}

# usage: mktt tt_id "tooltip message"
# <input ... $(ttip tt_id)>
ttip() {
	echo "onmouseover=\"popUp(event,'$1')\" onmouseout=\"popDown('$1')\""
}

menu_setup() {
	cat<<-EOF
		<script type="text/javascript">
		var menu = new Array();
		var men = {label:"Logout", url:"/cgi-bin/logout.cgi"};
		menu.push(men);
		men = {label:"Status", url:"/cgi-bin/status.cgi"};
		menu.push(men);
	EOF
	for i in Shortcuts $(cat Main.men); do
		echo -n "men = {label:\"$i\", smenu:["
		awk -F\| '{printf("{item:\"%s\", url:\"%s\"},\n", $1, $2)}' $i*.men
		cat<<-EOF
			]};
			menu.push(men);
		EOF
	done
	echo "menuSetup(\"$1\",\"$2\");"
	echo "</script>"
}

load_thm() {
	SCRIPTS=/scripts
	if test -f /usr/www/$SCRIPTS/$1; then
		while read ln; do
			if echo $ln | grep -q .js; then
				echo "<script type=\"text/javascript\" src=\"$SCRIPTS/$ln\"></script>"
			elif echo $ln | grep -q .css; then
				echo "<link rel=\"stylesheet\" type=\"text/css\" href=\"$SCRIPTS/$ln\">"
			elif echo $ln | grep -q .thm; then
				load_thm $ln
			fi
		done < /usr/www/$SCRIPTS/$1
	fi
}

# args: title [onload action]
write_header() {
	firstboot
	HTML_HEADER_DONE="yes"

	echo -e "Content-Type: text/html; charset=UTF-8\r\n\r"
	cat<<-EOF
		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html>
		<head profile="http://www.w3.org/2005/10/profile">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<link rel="icon" type="image/png" href="../dns-323.png">
	EOF

	if ! loadsave_settings -st >/dev/null; then
		warn_tt="The following files have changed since the last save:<br>$(loadsave_settings -lc | sed -n 's/ /<br>/gp')"
		warn=$(cat<<-EOF
			<h5 class="error"><a  class="error" href="/cgi-bin/settings.cgi" $(ttip tt_settings)>
			When done you must <u>save settings</u>
			<img src="../help.png" width="11" height="11" alt="help"></a></h5>
			EOF
			)
	fi

	if test "$#" = 2; then act="onLoad=\"$2\""; fi

	hf=${0%.cgi}_hlp.html
	if test -f /usr/www/$hf; then
		hlp="<a href=\"../$hf\" $(ttip tt_help)><img src=\"../help.png\" alt=\"help\" border=0></a>"
	fi

	if test -s "$CONF_MISC"; then . $CONF_MISC; fi

	cat<<-EOF
		<title>$1</title>
		<style type="text/css">
			$(echo "$LOCAL_STYLE")
		</style>
		$(load_thm default.thm)
		</head>
		<body $act>
		$(menu_setup "top" "$TOP_MENU")
		$(mktt tt_help "Get a descriptive help")
		$(mktt tt_settings "$warn_tt")
		<h2 class="title">$1 $hlp</h2>
		$warn
		$firstmsg
	EOF
}

md5() {
cat<<-EOF
	<script type="text/javascript">
	// https://github.com/jbt/js-crypto/blob/master/md5-min.js
	md5=function(){
		for(var m=[], l=0; 64>l;)
			m[l] = 0|4294967296*Math.abs(Math.sin(++l));
		return function(c){
			var e,g,f,a,h=[];
			c = unescape(encodeURI(c));
			for(var b=c.length, k=[e=1732584193,g=-271733879,~e,~g], d=0; d<=b;)
				h[d>>2] |= (c.charCodeAt(d)||128)<<8*(d++%4);
			h[c=16*(b+8>>6)+14]=8*b;
			for(d=0; d<c; d+=16){
				b=k;
				for(a=0; 64>a;)
					b = [f=b[3],(e=b[1]|0)+((f=b[0]+[e&(g=b[2])|~e&f,f&e|~f&g,e^g^f,g^(e|~f)][b=a>>4]+(m[a]+(h[[a,5*a+1,3*a+5,7*a][b]%16+d]|0)))<<(b=[7,12,17,22,5,9,14,20,4,11,16,23,6,10,15,21][4*b+a++%4])|f>>>32-b),e,g];
				for(a=4; a;)
					k[--a] = k[a]+b[a]
			}
			for(c=""; 32>a;)
				c += (k[a>>3]>>4*(1^a++&7)&15).toString(16);
			return c
		}
	}()
	</script>
EOF
}
