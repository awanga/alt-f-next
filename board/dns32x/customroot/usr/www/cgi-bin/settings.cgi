#!/bin/sh

. common.sh
check_cookie

write_header "Settings Management"

res=$(loadsave_settings -ls)
for i in $res; do
	sets="$sets <option>$i</option>"
done	

cat<<-EOF
	<script type="text/javascript">
	function ask() {
		return confirm("Clearing settings will erase all saved configuration changes that you have made to the system since you start using it.\n\nPlease read the on-line help first.\n\nProceed?");
	}
	function load_ask() {
		return confirm("Loading settings might change the box name and IP.\n" +
			"You should afterwards restart all running services, so they will apply changes." + "\n\nContinue?");

	}
	function format_ask() {
		return confirm("Formating the Flash makes it loose all saved settings.\n" +
			"It might be necessary if Settings can't be saved or loaded." +
			"\n\nContinue?");

	}
	</script>
	<fieldset><legend>Flash Memory</legend>
	<form action="/cgi-bin/settings_proc.cgi" method="post">
	<input type=submit name=action value=SaveSettings><br><br>
	<select name=settings>
	<option value="">Select one</option>$sets</select>
	<input type=submit name=action value=LoadSettings onclick="return load_ask()"><br><br>
	<input type=submit name=action value=ClearSettings onclick="return ask()">
	<input type=submit name=action value=FormatFlashSettings onclick="return format_ask()">
	</form>
	</fieldset>

	<fieldset><legend>Computer Disk</legend>
<h4 class="warn">The settings file contains sensitive information such as usernames and passwords, keep it safe.</h4>
	<form action="/cgi-bin/settings_proc.cgi" method="post">
	Backup current settings to file: <input type=submit name=action value="Download">
	</form>

	<form action="/cgi-bin/settings_proc.cgi" method="post" enctype="multipart/form-data"><br>
	Load backup settings from file: <input type=file name=settings>
	<input type=submit name=action value="Upload" onclick="return load_ask()">
	</form>
	</fieldset>
	</body></html>
EOF

