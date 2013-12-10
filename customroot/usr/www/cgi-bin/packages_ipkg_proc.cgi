#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/ipkg.conf

#debug

change_feeds() {
	mv $CONFF $CONFF-
	for i in $(seq 1 $nfeeds); do
		eval $(echo feed=\$feed_$i)
		if test -z "$feed"; then continue; fi
		feed=$(httpd -d "$feed")
		eval $(echo cmt=\$dis_$i)
		if test -n "$cmt"; then cmt="#!#"; fi
		echo "${cmt}src feed_$i $feed" >> $CONFF
	done
	echo "dest /Alt-F /Alt-F" >> $CONFF
}

ipkg_cmd() {

	if test $1 = "-install"; then
		write_header "Installing Alt-F"
	elif test $1 = "install"; then
		write_header "Installing Alt-F package $2"
		opts="-force-defaults"
	elif test $1 = "upgrade"; then
		write_header "Upgrading all Alt-F packages"
		opts="-force-defaults"
	fi

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
	EOF

	echo "<pre>"

	ipkg $opts $1 $2
	if test $? = 0; then
		cat<<-EOF
			</pre>
			<p><strong>Success</strong>
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	else
		if test $1 = "-install"; then
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

	change_feeds

	ipkg_cmd -install $mp

elif test -n "$RemoveAll"; then

	write_header "Removing all Alt-F packages"

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
		<pre>
	EOF

	busy_cursor_start
	for i in  $(ls -r /Alt-F/etc/init.d/S* 2>/dev/null); do
		if test -f $i; then
			f=$(basename $i)
			rcscript=rc${f:3}
			$rcscript stop
			for i in $(seq 1 60); do
				if ! $rcscript status >& /dev/null; then
					break
				fi
				usleep 500000
			done
			if test "$i" -eq 60; then
				fail=yes
			fi
		fi
	done
	if test -n "$fail"; then
		echo "<p><strong>It was not possible to stop some services, continuing anyway...</strong>"
	fi
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

elif test -n "$Submit"; then
	change_feeds

fi

res=$(ipkg update)

if test $? != 0; then
	msg "$res"
fi

if test -n "$Remove"; then
	res=$(ipkg remove $Remove 2>&1 | sed -n '/^Package/,/^$/p')

	if test -n "$res"; then
		msg "$res"
	fi

elif test -n "$InstallAll"; then
	write_header "Installing all Alt-F packages"
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
	ipkg_cmd upgrade
fi

#enddebug
gotopage /cgi-bin/packages_ipkg.cgi



