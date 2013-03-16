#!/bin/sh

. common.sh
check_cookie

write_header "Settings Management"

if ! isflashed; then
	clear_dis="disabled"
fi

res=$(loadsave_settings -ls)
for i in $res; do
	sets="$sets <option>$i</option>"
done	

cat<<-EOF
	<script type="text/javascript">
	function ask() {
		return confirm("If rebooted without settings, the box will first try to use a DHCP assigned IP," + '\n' +
		 "and if not successful will try to find a free IP in the 192.168.1.254-240 range."); 
	}
	function load_ask() {
		return confirm("Loading settings might change the box name and IP." + '\n' +
			"You should afterwards restart all running services, so they will apply changes." +
			 '\n' + '\n' + "Continue?");

	}
	</script>

	<fieldset><legend><strong>Flash Memory</strong></legend>
	<form action="/cgi-bin/settings_proc.cgi" method="post">
	<input type=submit name=action value=SaveSettings><br><br>
	<select name=settings>
	<option value="">Select one</option>$sets</select>
	<input type=submit name=action value=LoadSettings onclick="return load_ask()"><br><br>
	<input type=submit $clear_dis name=action value=ClearSettings onclick="return ask()">
	</form>
	</fieldset><br>

	<fieldset><legend><strong>Computer Disk</strong></legend>
	<form action="/cgi-bin/settings_proc.cgi" method="post">
	Save current settings to file: <input type=submit name=action value="Download">
	</form>

	<form action="/cgi-bin/settings_proc.cgi" method="post" enctype="multipart/form-data"><br>
	Load settings from file: <input type=file name=uploadedfile>
	<input type=submit name=action value="Upload" onclick="return load_ask()">
	</form>
	</fieldset>
	</body></html>
EOF

