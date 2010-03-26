#!/bin/sh

. common.sh
check_cookie

write_header "Settings Management"

if test -f /tmp/firstboot; then
	cat<<-EOF
		<center>
		<h3>Welcome to your first login to Alt-F</h3>
		<h4>To finish setting up Alt-F, you should now save the changes
		that you have just made.</h4>
		<h4>You should do it whenever you want your changes to survive a box reboot.</h4>
		</center>
	EOF
fi

res=$(loadsave_settings -ls)

cat<<-EOF
	<script type="text/javascript">
	function ask() {
		return confirm("Don't clear the flash-saved settings if your box still boots from the vendor firmware," + '\n' +
		 "or the box might not boot up. Press Cancel." + '\n' + '\n' +
		 "Under Alt-F, without settings, the box will first try to use a DHCP assigned IP," + '\n' +
		 "and if not successful will try to find a free IP in the 192.168.1.254-240 range."); 
	}
	</script>
	<form name=frm action="/cgi-bin/settings_proc.cgi" method="post">
	<input type=submit name=action value=SaveSettings><br>
	<select name=settings>
	<option value="">Select one</option>
EOF

for i in $res; do
	echo "<option>$i</option>"
done	

cat<<-EOF
	</select><input type=submit name=action value=LoadSettings><br>
	<input type=submit name=action value=ClearSettings onclick="return ask()">
		<strong>Don't clear if the box still has the vendor firmware!</strong><br>
	</form></body></html>
EOF

