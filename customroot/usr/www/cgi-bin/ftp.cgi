#!/bin/sh

. common.sh
check_cookie
write_header "vsftpd server Setup"

mktt tt_jail "If checked, the user will be restricted to use only its own home folder."
mktt tt_wchroot "If checked, the user home folder is allowed to be writable<br>(except for the anonymous user)."
mktt tt_dusers "Space separated list of usernames to deny ftp access"
mktt tt_anon "Allow anonymous access (the password-less 'ftp' user)." 
mktt tt_anonf "Folder for the anonymous user.<br>Must not be writable (sub folders can be, but must be previously created.)"
mktt tt_impl "On port 990 only SSL protocol is expected.<br>For server mode a second server will be run."

mktt ftpi_tt "Inetd mode: vsftpd runs only when necessary, slower to start, conserves memory."
mktt ftps_tt "Server mode: vsfdtp always running, faster, always consuming memory<br>
(the ftp/ftps checkboxes in the inetd web page will be unchecked)."

CONFF=/etc/vsftpd.conf
CONFU=/etc/vsftpd.user_list
INETD_CONF=/etc/inetd.conf

# to remove after RC5
if grep -q 'listen=' $CONFF; then
	sed -i '/listen=/d' $CONFF
fi

hostip=$(ifconfig eth0 | awk '/inet addr/ { print substr($2, 6) }')

userdeny=""
if test -f $CONFU; then
	denyusers=$(cat $CONFU | tr '\n' ' ')
fi

if test -f $CONFF; then
	. $CONFF >& /dev/null
fi

anon_root=$(sed -n 's/anon_root=\(.*\)/\1/p' $CONFF)
anon_root=$(readlink -f "$anon_root")
anon_root=$(httpd -e "$anon_root")

ssl_en="disabled"
if test "$ssl_enable" = "yes"; then
	ssl_en_chk=checked
	ssl_en=""
fi
if test "$force_local_logins_ssl" = "yes"; then
	ssl_fl_chk=checked
fi
if test "$force_local_data_ssl" = "yes"; then
	ssl_fd_chk=checked
fi

anon="disabled"
if test "$anonymous_enable" = "yes"; then
	anon_en_chk=checked
	anon=""
fi
if test "$anon_upload_enable" = "yes"; then
	anon_up_chk=checked
fi

jail_en_chk=""
wchroot_en=disabled
if test "$chroot_local_user" = "yes"; then
	jail_en_chk=checked
	wchroot_en=""
fi

wchroot_chk=""
if test "$allow_writeable_chroot" = "yes"; then
	wchroot_chk=checked
fi

ssl_imp_chk=""
if grep -q "implicit_ssl=yes" $CONFF || grep -q '^ftps' $INETD_CONF ; then
	ssl_imp_chk=checked
fi

syslog_chk=""
if test "$syslog_enable" = "yes"; then
	syslog_chk=checked
fi

xferlog_chk=""
if test "$xferlog_enable" = "yes"; then
	xferlog_chk=checked
fi

ftp_inetd="checked"; ftp_server="";
if grep -qE '(^ftp|^ftps)' $INETD_CONF; then
	ftp_inetd=checked
else
	ftp_server=checked
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
			} else if (obj.name == 'ssl_enable') {
				document.ftpf.force_local_logins_ssl.disabled = st
				document.ftpf.force_local_data_ssl.disabled = st
			} else if (obj.name == 'chroot_local_user') {
				document.ftpf.allow_writeable_chroot.disabled = st
			}
		}
	</script>


	<form name="ftpf" action="/cgi-bin/ftp_proc.cgi" method="post">
	<table>
	<tr><td>Restrict folders:</td><td><input type=checkbox $jail_en_chk id=jail name=chroot_local_user value="yes" onchange="toogle('jail')" $(ttip tt_jail)></td></tr>
	<tr><td>Writable folders:</td><td><input type=checkbox $wchroot_en $wchroot_chk id=wchroot name=allow_writeable_chroot value="yes" $(ttip tt_wchroot)></td></tr>
	<tr><td>Disallow users:</td><td><input type=text name=denyusers value="$denyusers" $(ttip tt_dusers)></td></tr>
	<tr><td colspan=2><br></td></tr>

	<tr><td>Enable Anonymous:</td><td><input type=checkbox $anon_en_chk id=anon name=anonymous_enable value="yes" onchange="toogle('anon')" $(ttip tt_anon)></td></tr>
	<tr><td>Anonymous uploads:</td><td><input type=checkbox $anon $anon_up_chk name=anon_upload_enable value="yes"></td></tr>
	<tr><td>Anonymous folder:</td><td><input type=text $anon id=anon_dir name=anon_root value="$anon_root" $(ttip tt_anonf)>
		<input type=button name=browse onclick="browse_dir_popup('anon_dir')" value=Browse></td></tr>

	<tr><td colspan=2><br></td></tr>
	<tr><td>Enable SSL:</td><td><input type=checkbox $ssl_en_chk id=ssl name=ssl_enable value="yes"  onchange="toogle('ssl')"></td></tr>
	<tr><td>Force SSL logins:</td><td><input type=checkbox $ssl_en $ssl_fl_chk name=force_local_logins_ssl value="yes"></td></tr>
	<tr><td>Force SSL data:</td><td><input type=checkbox $ssl_en $ssl_fd_chk name=force_local_data_ssl value="yes"></td></tr>
	<tr><td>Implict SSL:</td><td><input type=checkbox $ssl_en $ssl_imp_chk name=implicit_ssl value="yes" $(ttip tt_impl)></td></tr>
	<tr><td colspan=2><br></td></tr>

	<tr><td>Log accesses:</td><td><input type=checkbox $xferlog_chk name=xferlog_enable value="yes"></td></tr>
	<tr><td>Log to syslog:</td><td><input type=checkbox $syslog_chk name=syslog_enable value="yes"></td></tr>
	<tr><td colspan=2><br></td></tr>

	<tr><td>inetd mode</td><td><input type=radio $ftp_inetd name=ftp_inetd value="inetd" $(ttip ftpi_tt)></td></tr>
	<tr><td>server mode</td><td><input type=radio $ftp_server name=ftp_inetd value="server" $(ttip ftps_tt)></td></tr>

	</table>
	<input type="hidden" name=from_url value="$HTTP_REFERER">
	<p><input type="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
