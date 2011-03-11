#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/ipkg.conf

#debug

ipkg_cmd() {

	if test $1 = "-install"; then
		write_header "Installing Alt-F"
	elif test $1 = "install"; then
		write_header "Installing Alt-F package $2"
	elif test $1 = "upgrade"; then
		write_header "Upgrading Alt-F package $2"
	fi

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
	EOF

	echo "<pre>"

	ipkg $1 $2
	if test $? = 0; then
		cat<<-EOF
			</pre>
			<p><strong>Success</strong>
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	else
		if test $1 == "-install"; then
			ipkg -clean
		fi

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
		msg "You must select a filesystem"
	fi

	part=$(httpd -d $part)
	mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)

	ipkg_cmd -install $mp 

elif test -n "$RemoveAll"; then

	write_header "Removing Alt-F packages"

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
		<pre>
	EOF

	busy_cursor_start
	ipkg -clean
	if test $? != 0; then
		cat<<-EOF
			</pre>
			<p><strong>Failed</strong>
			<input type="button" value="Back" onclick="err()">
		EOF
	else
		cat<<-EOF
			</pre>
			<p><strong>Success</strong>
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	fi

	busy_cursor_end

	echo "</body></html>"
	exit 0
fi

ipkg update >& /dev/null

if test -n "$Remove"; then
	res=$(ipkg remove $Remove | sed -n '/^Package/,/^$/p' | tr '\n' ' ')

	if test -n "$res"; then
		msg "$res"
	fi

elif test -n "$InstallAll"; then
	Write_header "Installing all Alt-F packages"
	echo "<pre>"
	for i in $(ipkg -V0 list | cut -f1 -d" "); do
		if ! ipkg -V0 list_installed | cut -f1 -d" " | grep -q $i; then
			ipkg install $i
		fi
	done 
	cat<<-EOF
		</pre>
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
			setTimeout("err()", 2000);
		</script>
		</body></html>
	EOF
	exit 0

elif test -n "$Install"; then
	ipkg_cmd install $Install

elif test -n "$Update"; then
	ipkg_cmd install $Update

elif test -n "$UpdateAll"; then
	ipkg_cmd upgrade all

elif test -n "$ChangeFeed"; then
	if ! grep -q '^#!#src Alt-F-' $CONFF; then
		sed -i '/^src Alt-F-/s|^.*$|#!#&|' $CONFF
	fi
	sed -i '/src feed_/d' $CONFF
	for i in $(seq 1 $nfeeds); do
		eval $(echo feed=\$feed_$i)
		if test -z "$feed"; then continue; fi
		feed="$(httpd -d $feed)"
		echo "src feed_$i $feed" >> $CONFF
	done

elif test -n "$DefaultFeed"; then
	if grep -q '^#!#src Alt-F-' $CONFF; then
		sed -i '/^src feed_/d' $CONFF
		sed -i '/^#!#.*/s|^#!#||' $CONFF
	fi
fi

#enddebug
gotopage /cgi-bin/packages_ipkg.cgi



