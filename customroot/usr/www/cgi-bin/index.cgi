#!/bin/sh

if test -n "$QUERY_STRING"; then		
	eval $(echo -n $QUERY_STRING |  sed -e 's/'"'"'/%27/g' |
		awk 'BEGIN{RS="?";FS="="} $1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')

	pg="$(httpd -d "$pg")"
fi

cat<<-EOF
	Content-Type: text/html; charset=UTF-8

	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	</head>
	<body>

	<a href="/cgi-bin/logout.cgi" target="content">Logout</a><br>
	<a href="/cgi-bin/status.cgi" target="content">Status</a><br>
EOF

echo "<a href=\"/cgi-bin/index.cgi?pg=setup\">Setup</a><br>"
if test "$pg" = "setup"; then
	cat<<-EOF
	&emsp;<a href="/cgi-bin/host.cgi" target="content">Host</a><br>
	&emsp;<a href="/cgi-bin/time.cgi" target="content">Time</a><br>
	&emsp;<a href="/cgi-bin/mail.cgi" target="content">Mail</a><br>
	&emsp;<a href="/cgi-bin/proxy.cgi" target="content">Proxy</a><br>
	&emsp;<a href="/cgi-bin/hosts.cgi" target="content">Hosts</a><br>
	&emsp;<a href="/cgi-bin/usersgroups.cgi" target="content">Users</a><br>
	EOF
fi

echo "<a href=\"/cgi-bin/index.cgi?pg=disk\">Disk</a><br>"
if test "$pg" = "disk"; then
	cat<<-EOF
	&emsp;<a href="/cgi-bin/diskutil.cgi" target="content">Utilities</a><br>
	&emsp;<a href="/cgi-bin/diskpart.cgi" target="content">Partition</a><br>
	&emsp;<a href="/cgi-bin/diskmaint.cgi" target="content">Maintenance</a><br>
	&emsp;<a href="/cgi-bin/diskwiz.cgi" target="content">Wizard</a><br>
	EOF
fi

echo "<a href=\"/cgi-bin/index.cgi?pg=services\">Services</a><br>"
if test "$pg" = "services"; then
	cat<<-EOF
	&emsp;<a href="/cgi-bin/net_services.cgi" target="content">Network</a><br>
	&emsp;<a href="/cgi-bin/sys_services.cgi" target="content">System</a><br>
	&emsp;<a href="/cgi-bin/user_services.cgi" target="content">User</a><br>
	EOF
fi

echo "<a href=\"/cgi-bin/index.cgi?pg=packages\">Packages</a><br>"
if test "$pg" = "packages"; then
	cat<<-EOF
	&emsp;<a href="/cgi-bin/packages_ffp.cgi" target="content">ffp</a><br>
	&emsp;<a href="/cgi-bin/packages_ipkg.cgi" target="content">Alt-F</a><br>
	EOF
fi

echo "<a href=\"/cgi-bin/index.cgi?pg=system\">System</a><br>"
if test "$pg" = "system"; then
	cat<<-EOF
	&emsp;<a href="/cgi-bin/sys_utils.cgi" target="content">Utilities</a><br>
	&emsp;<a href="/cgi-bin/settings.cgi" target="content">Settings</a><br>
	&emsp;<a href="/cgi-bin/firmware.cgi" target="content">Firmware</a><br>
	EOF
fi

echo "</body></html>"

