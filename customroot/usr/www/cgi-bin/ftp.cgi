#!/bin/sh

. common.sh
check_cookie
write_header "vsftpd server Setup"

CONFF=/etc/vsftpd.conf

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')
network=$(echo $hostip | awk -F. '{printf "%d.%d.%d.", $1,$2,$3}')

if false; then
	CONFO=/etc/ssl/openssl.cnf
	countryName_default=AU
	stateOrProvinceName_default=Some-State
	localityName_default=Oporto
	organizationalUnitName_default=Sales
	commonName_default=DNS-323
	emailAddress_default=foo@po

	echo "<pre>"
		for i in $(eatspaces "$(grep '^[a-zA-Z]*_default.*=' $CONFO)"); do eval $i; done 
	echo "</pre>"
fi

if test -f $CONFF; then
	. $CONFF
fi

ssl_en="disabled"
if test "$ssl_enable" = "YES"; then
	ssl_en_chk=checked
	ssl_en=""
fi
if test "$force_local_logins_ssl" = "YES"; then
	ssl_fl_chk=checked
fi
if test "$force_local_data_ssl" = "YES"; then
	ssl_fd_chk=checked
fi

anon="disabled"
if test "$anonymous_enable" = "YES"; then
	anon_en_chk=checked
	anon=""
fi
if test "$anon_upload_enable" = "YES"; then
	anon_up_chk=checked
fi

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
		    start_dir = document.getElementById(input_id).value;
		    if (start_dir == "")
		    	start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function toogle(id) {
			obj = document.getElementById(id)
			st = ! obj.checked
			if (obj.name == 'anonymous_enable') {
				document.ftpf.anon_upload_enable.disabled = st
				document.ftpf.anon_root.disabled = st
				document.ftpf.browse.disabled = st
			} else {
				document.ftpf.force_local_logins_ssl.disabled = st
				document.ftpf.force_local_data_ssl.disabled = st
			}
		}
	</script>


	<form name="ftpf" action="/cgi-bin/ftp_proc.cgi" method="post">
	<table>

	<tr><td>Enable Anonymous:</td><td><input type=checkbox $anon_en_chk id=anon name=anonymous_enable value="YES" onchange="toogle('anon')"></td></tr>
	<tr><td>Anonymous uploads:</td><td><input type=checkbox $anon $anon_up_chk name=anon_upload_enable value="YES"></td></tr>
	<tr><td>Anonymous Directory:</td><td><input type=text $anon id=anon_dir name=anon_root value="$(readlink -f $anon_root)"></td>
		<td><input type=button name=browse onclick="browse_dir_popup('anon_dir')" value=Browse></td></tr>

	<tr><td><br></td></tr>
	<tr><td>Enable SSL:</td><td><input type=checkbox $ssl_en_chk id=ssl name=ssl_enable value="YES"  onchange="toogle('ssl')"></td></tr>
	<tr><td>Force SSL logins:</td><td><input type=checkbox $ssl_en $ssl_fl_chk name=force_local_logins_ssl value="YES"></td></tr>
	<tr><td>Force SSL data:</td><td><input type=checkbox $ssl_en $ssl_fd_chk name=force_local_data_ssl value="YES"></td></tr>

	<tr><td><br></td></tr>
	<tr><td></td><td><input type="submit" value="Submit">$(back_button)</td></tr>
	</form>
	</body></html>
EOF



