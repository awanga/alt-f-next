#!/bin/sh
. common.sh

check_cookie
write_header "ipkg Package Manager"

#debug

s="<strong>"
es="</strong>"

if ! test -f /Alt-F/usr/bin/ipkg-cl; then

	disks=$(ls /dev/sd?) >/dev/null 2>&1

	if test -z "$disks"; then
		echo "<br> $s No disks found! $es <br>"
		echo "</body></html>"
		exit 1
	fi

	cat<<-EOF
		<h4>No ipkg instalation found, install ipkg in:</h4>
		<form action="/cgi-bin/packages_ipkg_proc.cgi" method=post>
	EOF
	select_part
	echo "</select><input type=submit name=install value=Install>
	</form></body></html>"

else

	IFS=" - "

	apkg=""
	tf1=$(mktemp -t)
	ipkg-cl -V 0 list > $tf1
	while read pkg ver desc; do
		eval ver_$pkg="$ver"
		apkg="$apkg $pkg"
	done < $tf1

	cat <<-EOF
		<form action="/cgi-bin/packages_ipkg_proc.cgi" method=post>
		<fieldset><legend> $s Installed Packages $es</legend>
		<table><tr>
			<th>Name</th><th>Version</th><th></th><th></th><th>Description</th>
		</tr>
	EOF
	
	update=""
	tf2=$(mktemp -t)
	ipkg-cl -V 0 list_installed > $tf2
	while read pkg ver desc; do
		apkg=$(echo $apkg | sed 's/'$pkg'//')
		echo "<tr><td>$pkg</td><td>$ver</td>
			<td><input type=submit name=$pkg value=Remove></td>"
		if test $(eval echo \$ver_$pkg) != "$ver"; then
			echo "<td><input type=submit name=$pkg value=Update></td>"
			update=1
		else
			echo "<td></td>"
		fi
		desc=$(ipkg-cl -V 0 info $pkg | grep Description | cut -c 14-)
		echo "<td>$desc</td></tr>"		
	done < $tf2
	
	if test -n "$update"; then
		echo "<tr><td></td><td></td><td></td>
		<td><input type=submit name=updateall value=UpdateAll></td></tr>"
	fi

	cat <<-EOF
		</table></fieldset>
		<br><fieldset><legend> $s Available Packages $es </legend>
		<table><tr>
			<th>Name</th><th>Version</th>
			<th></th><th>Description</th>
		</tr>
	EOF
				
	while read pkg ver desc; do
		echo $apkg | grep -q "$pkg"
 		if test $? = 0; then
 			echo "<tr><td>$pkg</td><td>$ver</td>
				<td><input type=submit name=$pkg value=Install></td>
				<td>$desc</td></tr>"
		fi
	done < $tf1

	cat <<-EOF
		</table></fieldset><br>
		<input type=submit name=updatelist value=UpdateList>
		<input type=submit name=configfeed value=ConfigureFeed>
		</form>
	EOF

	rm $tf1 $tf2
fi

#enddebug
