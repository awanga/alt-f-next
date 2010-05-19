#!/bin/sh

. common.sh
check_cookie

write_header "Mail Setup"

CONFF=/etc/msmtprc

parse() {
	while read key value; do
		if test -n "$key" -a -n "$value" -a ${key###} = $key; then
			eval "$key=$value"
		fi
	done < $1
}

parse $CONFF

if test "$tls" = "on"; then tlsf=checked; fi
if test "$auth" = "off"; then authf=checked; sipf=disabled; fi

cat<<-EOF
	<script type="text/javascript">
	function toogle(theform) {
		for (var i = 0; i < theform.length; i++) {
			if (theform.elements[i].id == "sip")
				theform.elements[i].disabled = theform.elements[i].disabled ? false : true;
		}
	}
	</script>

	<form name=authf action=mail_proc.cgi method="post" >
	<table>
	<tr><td>Server Name</td>
		<td><input type=text size=20 id=host name=host value=$host></td></tr>
	<tr><td>Server Port</td>
		<td><input type=text size=5 id=port name=port value=$port></td></tr>
	<tr><td></td><td>TLS/SSL<input type=checkbox $tlsf name=tls value="on">
		Anonymous<input type=checkbox $authf name=auth value="off" onchange="toogle(authf)"></td></tr>

	<tr><td><br></td></tr>

	<tr><td>Username</td>
		<td><input type=text size=20 id=sip $sipf name=user value=$user></td></tr>
	<tr><td>Password</td>
		<td><input type=password size=20 id=sip $sipf name=password value=$password></td></tr>

	<tr><td><br></td></tr>
	<tr><td>Send To</td>
		<td><input type=text size=20 name=to value=$from>
		<input type=submit name=submit value=Test>	
		</td></tr>

	<tr><td><br></td></tr>
	<tr><td></td>
		<td><input type=submit name=submit value=Submit></td></tr>

	</table></form></body></html>
EOF
