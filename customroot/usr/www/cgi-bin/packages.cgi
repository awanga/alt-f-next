#!/bin/sh

. common.sh
check_cookie

write_header "Package Manager"


cat<<-EOF
	<table align=center><tr><td>
	<form action="/cgi-bin/packages_ffp.cgi" method="post">
	<input type=submit name=action value="ffp packages">
	</form>
	</td><td>
	<form action="/cgi-bin/packages_ipkg.cgi" method="post">
	<input type=submit name=action value="ipkg packages">
	</form></td></tr></table>
	</body></html>
EOF

