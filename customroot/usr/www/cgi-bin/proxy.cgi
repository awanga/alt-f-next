#!/bin/sh

. common.sh
check_cookie
write_header "Wget Proxy Setup"

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
	while read ln; do
		eval $(eatspaces $ln)
	done < $WGETCONF

	eval $(parse $http_proxy)
	http_srv="$srv"
	http_port="$prt"

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
		sipf = document.getElementById("proxyf");
		state = document.getElementById("useproxy").checked == true ? false : true;
		document.getElementById("anonproxy").disabled = state
		for (var i = 0; i < sipf.length; i++) {
			if (sipf.elements[i].id == "prx")
				sipf.elements[i].disabled = state;
		}

		state2 = document.getElementById("anonproxy").checked
		for (var i = 0; i < sipf.length; i++) {
			if (sipf.elements[i].id == "aprx")
				sipf.elements[i].disabled = state || state2;
		}
	}
	function atoogle() {
		sipf = document.getElementById("proxyf");
		state = document.getElementById("anonproxy").checked
		for (var i = 0; i < sipf.length; i++) {
			if (sipf.elements[i].id == "aprx")
				sipf.elements[i].disabled = state
		}
	}
	</script>

	<form id="proxyf" action="/cgi-bin/proxy_proc.cgi" method="post">
	<table>
	<tr><td>Use a Proxy</td><td><input type=checkbox $PRXCHK id="useproxy" name="useproxy" value="yes" onclick="toogle()"></td></tr>
	<tr><td>HTML Proxy Server:</td><td><input type=text $PRXEN id="prx" name="http_proxy" value="$http_srv"></td>
		<td>Port:</td><td><input type=text $PRXEN id="prx" name="http_port" value="$http_port"></td></tr>
	<tr><td>FTP Proxy Server:</td><td><input type=text $PRXEN id="prx" name="ftp_proxy" value="$ftp_srv"></td>
		<td>Port:</td><td><input type=text $PRXEN id="prx" name="ftp_port" value="$ftp_port"></td></tr>
	<tr><td><br></td></tr>
	<tr><td>Anonymous Proxy</td><td><input type=checkbox $APRXCHK id="anonproxy" name="useproxy" value="yes" onclick="atoogle()"></td></tr>
	<tr><td>Proxy Username:</td><td><input type=text $APRXEN $PRXEN id="aprx" name="proxy_user" value=$proxy_user></td></tr>
	<tr><td>Proxy Password:</td><td><input type=password $APRXEN $PRXEN id="aprx" name="proxy_password" value=$proxy_password></td></tr>

	<tr><td></td><td><input type="submit" value="Submit"></td></tr>
	</table>
	</form>
	</body></html>
EOF

