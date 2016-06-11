#!/bin/sh

. common.sh

check_cookie

RSITE=www.inreto.de
FSITE="http://$RSITE"
FDIR="dns323/fun-plug"

write_header "ffp Package Manager"
has_disks

if ! test -d /ffp/var/packages -o -d /ffp/funpkg/installed; then
	cat<<-EOF
		<h4>No ffp instalation found.</h4>
		<form action="/cgi-bin/packages_ffp_proc.cgi" method=post>
		<table>
		<tr><td>Install ffp-0.5 (stable)</td><td><input type=radio checked name=ffpver value=0.5></td></tr>
		<tr><td>Install ffp-0.7 (recent)</td><td><input type=radio name=ffpver value=0.7></td></tr>
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
	FFP_DIR="0.5"
	xtra_pkgs="$FSITE/$FDIR/0.5/extra-packages/All/"
	arch_ext=tgz
	spat='-*-*'
	gpat='-[^-]*-[^-]*$'
else
	ffpver="0.7"
	FFP_DIR="0.7/oabi"
	xtra_pkgs="$FSITE/$FDIR/0.7/oabi/extras/"
	arch_ext=txz
	spat='-*-oarm-*'
	gpat='-[^-]*-oarm-[^-]*$'
fi

	cat<<-EOF
		<script type="text/javascript">
			function ask_Uninstall() {
				return confirm("All ffp files will be erased." + '\n\n' + "You will have to reinstall ffp.");
			}
			function ask_Upgrade() {
				return confirm("The ffp folder will be renamed ffp-0.5." + '\n\n' + "If a folder named ffp-0.7 is found, it will be renamed ffp" + '\n' +  "and reused, otherwise you will have to reinstall and configure ffp.");
			}
			function ask_Downgrade() {
				return confirm("The ffp folder will be renamed ffp-0.7." + '\n\n' + "If a ffp-0.5 folder is found it will be renamed ffp and reused, otherwise you will have to reinstall and configure ffp.");
			}
		</script>
		<h4 class="warn">Warning: configuration files are overwritten when updating</h4>
	EOF

	if test "$ffpver" = "0.5"; then
		inst_pkg=$(ls /ffp/var/packages)
	else
		inst_pkg=$(ls /ffp/funpkg/installed)
	fi

	if ! nslookup $RSITE >& /dev/null; then
		echo '<center><h3 class="blue">You dont seem to have a working internet connection<br>
	or/and a name server configured.</h3></center>'
	fi

	if avail_pkg=$(wget --tries=1 --timeout=30 $FSITE/$FDIR/$FFP_DIR/packages/ $xtra_pkgs -O - 2>/dev/null); then
		avail_pkg=$(echo "$avail_pkg" | sed -n 's|<li>.*>[[:space:]]*\(.*\).'$arch_ext'.*|\1|p')
		avail_pkg=$(echo -e "$avail_pkg\n$inst_pkg" | sort -u)
	else
		echo "<center><h3 class=\"blue\">The ffp package server <a href=\"$FSITE\">$FSITE</a> is not responding</h3></center>'"
		noserver=y
	fi

	cat <<-EOF
		<form action="/cgi-bin/packages_ffp_proc.cgi" method=post>
		<input type=hidden name=ffpver value="$ffpver">
		<fieldset><legend>Installed Packages</legend><table>
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
	
	if test "$ffpver" = "0.5"; then
		op=Upgrade; to="ffp-0.7"
	else
		op=Downgrade; to="ffp-0.5"
	fi

	cat <<-EOF
		<tr><td colspan=3><br></td></tr>
		<tr><td><strong>Uninstall ffp-$ffpver</strong></td>
			<td colspan=2><input type=submit name=uninstall value="Uninstall" onclick="return ask_Uninstall()"></td></tr>
		<tr><td><strong>$op to $to</upgrade></td>
			<td colspan=2><input type=submit name=$op value="$op" onclick="return ask_$op()"></td></tr>
		</table></fieldset>
	EOF

	if test -z "$noserver"; then
		cat<<-EOF
		<fieldset><legend>
		<a href="$FSITE/$FDIR/$FFP_DIR/">
		<strong>Available ffp Packages</strong></a></legend><table>
		EOF
	
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
	fi
	
	echo "</table></fieldset></form></body></html>"
