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
	verbose="" # changed my mind
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
		msg "You must select a partition"
	fi

	part=$(httpd -d $part)
	mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)

	ipkg_cmd -install $mp 

elif test -n "$RemoveAll"; then
	for i in $(ipkg -V0 list_installed | cut -f1 -d" "); do
		if test "$i" != "ipkg"; then
			ipkg -force-depends remove $i >& /dev/null
		fi
	done
	ipkg remove ipkg >& /dev/null
	aufs.sh -u
	rm -rf $(readlink -f /Alt-F)
	rm -f /Alt-F
	gotopage /cgi-bin/packages_ipkg.cgi
fi

ipkg update >& /dev/null

if test -n "$Remove"; then
	#ipkg_cmd remove $Remove # returns 0 even when fails

	res=$(ipkg remove $Remove | sed -n '/^Package/,/^$/p' | tr '\n' ' ')

	if test -n "$res"; then
		msg "$res"
	fi

elif test -n "$InstallAll"; then
	html_header
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



