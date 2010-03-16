#!/bin/sh

. common.sh
check_cookie

write_header "Settings Management"

res=$(loadsave_settings -ls)

cat<<-EOF
	<script type="text/javascript">
	function ask() {
		return confirm("Don't clear the flash-saved settings if" + '\n' +
		 "your box still boots from the vendor firmware," + '\n' +
		 "or the box might not boot up. Press Cancel." + '\n' + '\n' +
		 "It's only safe to clear the flash-saved settings" + '\n' + 
		 "if you have flashed Alt-F." + '\n' +
		 "Without settings, the box will use a DHCP assigned IP," + '\n' +
		 "or a free IP in the 192.168.1.254-240 range."); 
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

