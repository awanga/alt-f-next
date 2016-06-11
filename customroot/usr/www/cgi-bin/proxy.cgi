#!/bin/sh

. common.sh
check_cookie
write_header "Wget Proxy Setup"
check_https

WGETCONF=/etc/wgetrc

parse() {
	echo $1 | awk '{
		nf = split($0,a,":")
		if (nf == 1)
			printf "srv=%s", a[1]
		else if (nf == 3)
			printf "srv=%s; prt=%s", substr(a[2],3), a[3]
		else if (nf == 2 && (a[1] == "ftp" || a[1] == "http"))
			printf "srv=%s", substr(a[2],3)
		else printf "srv=%s; prt=%s", a[1], a[2]}'
}

PRXEN=disabled
PRXCHK=""
if test -e $WGETCONF; then
	while read -r ln; do
		if echo "$ln" | grep -q ^proxy_password; then
			pass=$(echo $ln | sed -n '/^proxy_password/s/proxy_password=//p')
			proxy_password=$(httpd -e "$pass")
		else
			eval $(eatspaces "$ln")
		fi
	done < $WGETCONF

	eval $(parse $http_proxy)
	http_srv="$srv"
	http_port="$prt"

	srv="";prt=""
	eval $(parse $https_proxy)
	https_srv="$srv"
	https_port="$prt"

	srv="";prt=""
	eval $(parse $ftp_proxy)
	ftp_srv="$srv"
	ftp_port="$prt"

	if test "$use_proxy" = "on"; then
		PRXEN=""; PRXCHK="checked"
		if test -z "$proxy_user" -a -z "$proxy_password"; then
			APRXCHK="checked"; APRXEN="disabled"
		fi
	fi
fi

cat<<-EOF
	<script type="text/javascript">
	function toogle() {
		state = document.getElementById("usepr").checked == true ? false : true;
		for (i=1; i<7; i++) {
			obj = document.getElementById("usepr" + i);
			obj.disabled = state
		}
		atoogle()
		document.getElementById("anonpr").disabled = state
	}
	function atoogle() {
		state1 = document.getElementById("anonpr").checked == true ? true : false
		state2 = document.getElementById("usepr").checked == true ? false : true
		for (i=1; i<3; i++) {
			obj = document.getElementById("anonpr" + i);
			obj.disabled = state1 || state2
		}
	}
	</script>

	<form id="proxyf" action="/cgi-bin/proxy_proc.cgi" method="post">
	<table>
	<tr><td>Use a Proxy</td><td><input type=checkbox $PRXCHK id="usepr" name="useproxy" value="yes" onclick="toogle()"></td></tr>

	<tr><td>HTTP Proxy Server:</td><td><input type=text $PRXEN id="usepr1" name="http_proxy" value="$http_srv">
		Port:<input type=text size=6 $PRXEN id="usepr2" name="http_port" value="$http_port"></td></tr>

	<tr><td>HTTPS Proxy Server:</td><td><input type=text $PRXEN id="usepr3" name="https_proxy" value="$https_srv">
		Port:<input type=text size=6 $PRXEN id="usepr4" name="https_port" value="$https_port"></td></tr>

	<tr><td>FTP Proxy Server:</td><td><input type=text $PRXEN id="usepr5" name="ftp_proxy" value="$ftp_srv">
		Port:<input type=text size=6 $PRXEN id="usepr6" name="ftp_port" value="$ftp_port"></td></tr>
	<tr><td colspan=2><br></td></tr>
	<tr><td>Anonymous Proxy</td><td><input type=checkbox $APRXCHK id="anonpr" name="anonproxy" value="yes" onclick="atoogle()"></td></tr>
	<tr><td>Proxy Username:</td><td><input type=text $APRXEN $PRXEN  id="anonpr1" name="proxy_user" value="$proxy_user"></td></tr>
	<tr><td>Proxy Password:</td><td><input type=password $APRXEN $PRXEN id="anonpr2" name="proxy_password" value="$proxy_password"></td></tr>
	</table>
	<p><input type="submit" value="Submit">
	</form></body></html>
EOF

