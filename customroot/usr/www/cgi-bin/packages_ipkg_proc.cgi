#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/ipkg.conf

#debug

ipkg_cmd() {

	html_header

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
	EOF

	echo "<pre>"
	if test $1 != "-install"; then
		verbose="-verbose_wget"
	fi
	ipkg $verbose $1 $2
	if test $? = 0; then
		cat<<-EOF
			</pre>
			<p><strong>Success</strong>
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	else
		cat<<-EOF
			</pre>
			<p><strong>An error occurred </strong>
			<input type="button" value="Back" onclick="err()"></p>
		EOF
	fi
	echo "</body></html>"
	exit 0
}

if test "$install" = "Install"; then

	if test "$part" = "none"; then
		msg "You must select a partition"
	fi

	part=$(httpd -d $part)
	mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)

	ipkg_cmd -install $mp 

fi

ipkg -V0 update

if test -n "$Remove"; then
	#ipkg_cmd remove $Remove # returns 0 even when fails

	res=$(ipkg remove $Remove | sed -n '/^Package/,/^$/p' | tr '\n' ' ')

	if test -n "$res"; then
		msg "$res"
	fi

elif test -n "$Install"; then
	ipkg_cmd install $Install

elif test -n "$Update"; then
	ipkg_cmd install $Update

elif test -n "$UpdateAll"; then
	ipkg_cmd upgrade all

elif test -n "$ConfigureFeed"; then
	msg "Not yet"
fi

#enddebug
gotopage /cgi-bin/packages_ipkg.cgi



