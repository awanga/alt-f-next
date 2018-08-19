#!/bin/sh

. common.sh

check_cookie

write_header "ffp Package Manager"
has_disks

. /etc/misc.conf

if test -z "$FFPSITE"; then
	FFPSITE="http://www.inreto.de/dns323/fun-plug"
	echo FFPSITE=$FFPSITE >> /etc/misc.conf
fi

FPROTO=$(echo $FFPSITE | sed -n 's|\(.*\)://.*|\1|p')
RSITE=$(echo $FFPSITE | sed -n 's|.*://\([^/]*\).*|\1|p')
FDIR=$(echo $FFPSITE | sed -n 's|.*://[^/]*/\(.*\)|\1|p')
FSITE="$FPROTO://$RSITE"

if test -z "$FPROTO" -o -z "$RSITE" -o -z "$FDIR"; then
	errmsg="<center><h3 class="red">Invalid download site</h3></center>"
fi

disclaimer="<h4 class="warn">Warning: ffp is alien to Alt-F, conflicts might arise.<br>
	Packages configuration files have to be manually edited,<br>
	configuration files are overwritten when updating,<br>
	and packages dependencies are not automatically handled.<br></h4>"

if ! test -d /ffp/var/packages -o -d /ffp/funpkg/installed; then
	cat<<-EOF
		$disclaimer
		<h4>No ffp instalation found.</h4>
		$errmsg
		<form action="/cgi-bin/packages_ffp_proc.cgi" method=post>
		<table>
		<tr><td>Install ffp-0.5</td><td><input type=radio checked name=ffpver value=0.5></td></tr>
		<tr><td>Install ffp-0.7</td><td><input type=radio name=ffpver value=0.7></td></tr>
		<tr><td>from</td><td><input type=text size=40 name=ffpsite value="$FFPSITE"></td></tr>
		<tr><td>into</td><td>$(select_part)</td></tr>
		<tr><td></td><td><input type=submit name=install value=Install></td></tr>
		</table></form></body></html>
	EOF
	exit 0
fi

if test -s /ffp/etc/ffp-version; then
	. /ffp/etc/ffp-version
else
	FFP_VERSION=0.5
	echo FFP_VERSION=0.5 > /ffp/etc/ffp-version
fi

if test "$FFP_VERSION" = "0.5"; then
	ffpver="0.5"
	FFP_DIR="$ffpver"
	xtra_pkgs="$FSITE/$FDIR/$ffpver/extra-packages/All/"
	inst_pkg=$(ls /ffp/var/packages)
	arch_ext=tgz
	spat='-*-*'
	gpat='-[^-]*-[^-]*$'
	op=Upgrade; to="ffp-0.7"
else
	ffpver="0.7"
	arch=$FFP_ARCH
	if test "$arch" = "oarm"; then
		warnmsg='<h4 class="warn">Warning: you are using the obsolete "oabi/oarm" architecture.</h4>'
	fi
	FFP_DIR="$ffpver/$arch" 
	inst_pkg=$(ls /ffp/funpkg/installed)
	arch_ext=txz
	spat='-*-'$arch'-*'
	gpat='-[^-]*-'$arch'-[^-]*$'
	op=Downgrade; to="ffp-0.5"
fi

cat<<-EOF
	<script type="text/javascript">
		function ask_Uninstall() {
			return confirm("All ffp files will be erased." + '\n\n' + "You will have to reinstall ffp.");
		}
		function ask_Upgrade() {
			return confirm("The current ffp folder will be renamed ffp-0.5." + '\n\n' + "If a folder named ffp-0.7 is found, it will be renamed ffp" + '\n' +  "and reused, otherwise you will have to reinstall and configure ffp.");
		}
		function ask_Downgrade() {
			return confirm("The current ffp folder will be renamed ffp-0.7." + '\n\n' + "If a ffp-0.5 folder is found it will be renamed ffp and reused, otherwise you will have to reinstall and configure ffp.");
		}
	</script>
	$disclaimer
	$errmsg
	$warnmsg
EOF

if ! nslookup $RSITE >& /dev/null; then
	echo "<center><h3 class=\"red\">Server '$RSITE' not found</h3></center>"
fi

if avail_pkg=$(wget --tries=1 --timeout=30 $FSITE/$FDIR/$FFP_DIR/packages/ $xtra_pkgs -O - 2>/dev/null); then
	avail_pkg=$(echo "$avail_pkg" | sed -n 's|.*<a href="\(.*\).'$arch_ext'".*|\1|p')
	avail_pkg=$(echo -e "$avail_pkg\n$inst_pkg" | sort -u)
else
	echo "<center><h3 class=\"red\">Error getting packages from <a href=\"$FFPSITE\">$FFPSITE</a></h3></center>'"
	noserver=y
fi

cat <<-EOF
	<form action="/cgi-bin/packages_ffp_proc.cgi" method=post>
	<input type=hidden name=ffpver value="$ffpver">
	
	<fieldset><legend>Package Feed</legend><table>
	<tr><td>Download site</td><td><input type=text size=40 name=ffpsite value="$FFPSITE"><input type=submit name=feed value="Change"</td></tr>
	<tr><td>Uninstall ffp-$ffpver</td>
		<td colspan=2><input type=submit name=uninstall value="Uninstall" onclick="return ask_Uninstall()"></td></tr>
	<tr><td>$op to $to</upgrade></td>
		<td colspan=2><input type=submit name=$op value="$op" onclick="return ask_$op()"></td></tr>
	</table></fieldset>

	<fieldset><legend>Installed ffp Packages</legend><table>
EOF

for i in $inst_pkg; do
	base_name=${i%$spat}
	if test -z "$noserver"; then
		plnk="<a href="/cgi-bin/embed.cgi?name=ffp+$base_name?site=$(url_encode $FSITE/$FDIR/$FFP_DIR/PACKAGES.html#$base_name)">$i</a>"
	else
		plnk=$base_name
	fi
	cat<<-EOF
		<tr><td>$plnk</td>
		<td><input type=submit name="$i" value="Remove"></td>
	EOF

	updates=$(echo "$avail_pkg" | grep $base_name$gpat)
	update_name=$(echo "$updates" | tail -1)
	if test -n "$update_name" -a "$update_name" != $i; then
		echo "<td><input type=submit name=\"$update_name\" value=\"Update\">to $update_name</td>"
	else
		echo "<td></td>"
	fi
	for j in $updates; do
		avail_pkg=$(echo "$avail_pkg" | sed "/$j/d")
	done

	echo "</tr>"
done

echo "</table></fieldset>"

if test -z "$noserver"; then
	echo "<fieldset><legend>Available ffp Packages</legend><table>"

	for i in $avail_pkg; do
		base_name=${i%$spat}

		updates=$(echo "$avail_pkg" | grep $base_name$gpat)
		if test -z "$updates"; then continue; fi
		update_name=$(echo "$updates" | tail -1)
		for j in $updates; do
			avail_pkg=$(echo "$avail_pkg" | sed "/$j/d")
		done
		cat<<-EOF
			<tr><td><a href="/cgi-bin/embed.cgi?name=ffp+$base_name?site=$(url_encode $FSITE/$FDIR/$FFP_DIR/PACKAGES.html#$base_name)">$update_name</a></td>
			<td><input type=submit name="$update_name" value="Install"></td></tr>
		EOF
	done
	echo "</table></fieldset>"
fi

echo "</form></body></html>"
