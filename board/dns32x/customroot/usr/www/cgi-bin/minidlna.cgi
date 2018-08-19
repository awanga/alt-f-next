#!/bin/sh

. common.sh
check_cookie

write_header "miniDLNA Setup"

mktt rescan_tt "Forces a rescan of all shares on service start.<br>It can take a lot of time, use only if necessary."

CONFF=/etc/minidlna.conf

if test -e $CONFF; then
	friendly_name=$(awk -F= '/^friendly_name/{printf "%s", $2}' $CONFF)
	enable_tivo=$(awk -F= '/^enable_tivo/{printf "%s", $2}' $CONFF)
	strict_dlna=$(awk -F= '/^strict_dlna/{printf "%s", $2}' $CONFF)
	presentation_url=$(awk -F= '/^presentation_url/{printf "%s", $2}' $CONFF)
	force_rescan=$(awk -F= '/^#force_rescan/{printf "%s", $2}' $CONFF)
	MDLNA_DIR=$(awk -F= '/^media_dir/{printf "%s;", $2}' $CONFF)
fi

if test "$force_rescan" = "yes"; then RESCAN_CHK=checked; fi
if test "$enable_tivo" = "yes"; then TV_CHK=checked; fi
if test "$strict_dlna" = "yes"; then STRICT_CHK=checked; fi
if test -z "$friendly_name" -o "$friendly_name" = "miniDLNA"; then friendly_name="miniDLNA on $(hostname)"; fi
if test -n "$presentation_url"; then XBOX_CHK=checked; fi
 
cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
			start_dir = document.getElementById(input_id).value;
			if (start_dir == "")
				start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
	</script>

	<form name=minidlna action=minidlna_proc.cgi method="post" >
	<table><tr><th>Type</th><th>Share Folder</th><th></th></tr>
EOF

OIFS="$IFS"; IFS=";"; k=1

for i in $MDLNA_DIR; do

	achk=""; vchk=""; pchk="";
	if echo $i | grep -q ^/ ; then
		mdir=$i
	else
		mdir=${i:2}
		mtype=${i:0:1}
		case $mtype in
			A|a) achk=selected ;;
			V|v) vchk=selected ;;
			P|p) pchk=selected ;;
		esac
	fi

	otype="<option>Any</option>
	<option value=A $achk>Audio</option>
	<option value=V $vchk>Video</option>
	<option value=P $pchk>Pictures</option>"

	cat<<-EOF
		<tr>
		<td align=center><select name=stype_$k>$otype</select></td>
		<td><input type=text size=32 id="conf_dir_$k" name="sdir_$k" value="$mdir"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done
IFS="$OIFS"

for j in $(seq $k $((k+2))); do
	otype="<option>Any</option><option value=A>Audio</option>
		<option value=V>Video</option><option value=P>Pictures</option>"
	cat<<-EOF
		<tr>
		<td align=center><select name=stype_$j>$otype</select></td>
		<td><input type=text size=32 id="conf_dir_$j" name="sdir_$j" value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done

cat<<-EOF
	</table><p><table>
	<tr><td>Server Name</td><td><input type=text name=friendly_name value="$friendly_name"></td></tr>
	<tr><td>Rescan shares</td><td><input type=checkbox $RESCAN_CHK=checked name=force_rescan value=yes $(ttip rescan_tt)></td></tr>
	<tr><td>Strict DLNA</td><td><input type=checkbox $STRICT_CHK name=strict_dlna value=yes></td></tr>
	<tr><td>TiVo Support</td><td><input type=checkbox $TV_CHK name=enable_tivo value=yes></td></tr>
	<tr><td>Xbox Support</td><td><input type=checkbox $XBOX_CHK name=enable_xbox value=yes></td></tr>
	</table>
	<input type=hidden name=cnt value=$j>
	<input type=hidden name=port value=$port>
	<p><input type=submit value=Submit>$(back_button)
	<input type=submit name="webPage" value="WebPage">
	</form></body></html>
EOF
