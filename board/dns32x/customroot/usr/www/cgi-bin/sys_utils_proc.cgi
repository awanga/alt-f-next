#!/bin/sh

. common.sh
check_cookie

if test "${CONTENT_TYPE%;*}" = "multipart/form-data"; then
	if ! upfile=$(upload_file); then
		msg "Error: Uploading failed: $upfile"
		exit 0
	fi
	action="UploadTheme"
else
	read_args
fi

CONFM=/etc/misc.conf
THM_DIR=/usr/www/scripts

#debug

# $1 log file, $2 kind, $3 header
showlog() {

	if test -n "$Download"; then
		if test "$(dirname $1)" = "/tmp"; then
			mv $1 /tmp/$2.log
			download_file /tmp/$2.log
			rm /tmp/$2.log
		else
			download_file $1
		fi
		exit 0
	fi

	if test -n "$Clear"; then
		echo -n > $1
		gotopage /cgi-bin/sys_utils.cgi
	fi

	if test "$2" != "SystemLog" -a "$2" != "Processes" -a \
		"$2" != "KernelLog" -a "$2" != "SystemConf"; then 
			clearbutton="<input type=submit name=\"$2\" value=\"Clear\">"
	fi

	write_header "$3"
	mktt filter_tt "Enter a search string (or a grep regular expression)"

	echo "<pre>"

	if test -n "$filter_str"; then
		pat=$(httpd -d $filter_str)
		cat $1 | grep -iE "$pat"
	else
		cat $1
	fi

	cat<<-EOF
		</pre>
		<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
		<input type=submit name="$1" value="Download">
		Filter: <input type=text name=filter_str value="$pat" onkeypress="return event.keyCode != 13" $(ttip filter_tt)>
		<input type=submit name="$2" value="Refresh">
		$clearbutton
		$(back_button)
		<input type=hidden name=logfile value="$2">
		</form></body></html>
	EOF
}

lreboot() {
	html_header
	cat<<-EOF
		<script type="text/javascript">

		var count = 20;
		var server = location.protocol + "//" + location.host
		var page = server + "/cgi-bin/status.cgi"
		var testimg = server + "/help.png?" + Math.random()

		function testServer() {    
			var img = new Image()

			img.onload = function() {
				if (img.naturalHeight > 0)
					window.location.assign(page)
			}

			img.onerror = function() {
				if (count) {
					count--
					setTimeout(testServer, 3000)
				} else
					window.location.assign(page)
			}
			img.src = testimg
		}

		setTimeout(testServer, 20000)

		</script>

		<br><br><fieldset><legend>The box is rebooting</legend>
		<center><h4>
		$(wait_count_start "Waiting 60 seconds")
		</h4></center></fieldset>
		</body></html>
	EOF
	/sbin/reboot
	exit 0
}

err() {
	rm -f $upfile
	msg "Error: $1"
	exit 0
}

if test -n "$theme"; then
	action="Theme"
elif test -n "$Refresh"; then
	action="$Refresh"
elif test -n "$Clear"; then
	action="$Clear"
elif test -n "$Download"; then
	action="$logfile"
elif test -n "$logaction" -a "$logaction" != "Select+one"; then
	action="$logaction"
fi

case "$action" in
	Reboot) lreboot ;;

	RebootAndCheck)
		loadsave_settings -sb
		lreboot
		;;

	Poweroff)
		html_header "<br><br>The box is being powered off."
		echo "</body></html>"
		/usr/sbin/poweroff
		exit 0
		;;

	Submit)
		sed -i /POWERUP_AFTER_POWER_FAIL/d $CONFM
		if test -n "$set_apr"; then
			echo POWERUP_AFTER_POWER_FAIL=1 >> $CONFM
		fi

		sed -i /POWERUP_ON_WOL/d $CONFM
		if test -n "$set_wol"; then
			echo POWERUP_ON_WOL=1 >> $CONFM
		fi

		TF=$(mktemp -t)
		crontab -l > $TF 2> /dev/null
		if test -z "$set_spd"; then
			sed -i '\|/usr/sbin/poweroff|d' $TF
			sed -i '/POWERDOW_SET/d' $CONFM
		else
			at=$(httpd -d "$spd_at")
			if echo $at | grep -q ':'; then
				hour=${at%%:*}
				if test -z "$hour"; then hour='*'; fi
				min=${at##*:}
				if test -z "$min"; then min='0'; fi
			else
				hour=$at
				min=0
			fi

			wday=$(httpd -d "$spd_wday")
			if test "${wday:0:1}" = "d"; then
				mday=${wday:1}
				wday='*'
			else
				mday='*'
			fi
			if test -z "$wday" -o -z "$hour"; then
				echo "invalid At or When format"
			fi

			sed -i '\|/usr/sbin/poweroff|d' $TF
			echo "$min $hour $mday * $wday /usr/sbin/poweroff #!# Alt-F cron" >> $TF
			sed -i '/POWERDOW_SET/d' $CONFM
			echo "POWERDOW_SET=\"$min $hour $mday * $wday\"" >> $CONFM
		fi
		crontab $TF 2> /dev/null
		rm -f $TF

		sed -i -e /POWERUP_ALARM_SET/d -e /POWERUP_ALARM_REPEAT/d $CONFM
		if test -n "$set_spu"; then
			when=$(httpd -d "$spu_when" | awk -F- '{printf("%d %d", $2, $3)}')
			at=$(httpd -d "$spu_at" | awk -F: '{printf("%d %d", $1, $2)}')
			echo POWERUP_ALARM_SET=\"$when $at\" >> $CONFM

			rep=$(httpd -d "$spu_rep")
			rl=$( expr ${#rep} - 1)
			if test ${rep:0:1} != '+' -o \( ${rep:$rl} != 'd' -a ${rep:$rl} != 'm' \); then
				msg "Invalid repetition format"
			fi
			rl=$((--rl))
			if ! isnumber ${rep:1:$rl}; then
				msg "Invalid repetition format"
			fi
			echo POWERUP_ALARM_REPEAT=$rep >> $CONFM
		fi
		rcpower start >& /dev/null
		;;

	ClearPrintQueues)
		#lpq -d doesnt work
		for i in $(cut -f1 -d"|" /etc/printcap 2>/dev/null); do
			if test -d /var/spool/lpd/$i; then
				mkdir -p /var/spool/lpd/$i/.lockdir >& /dev/null  # see /usr/bin/print
				if test -n "$(pidof print)"; then kill $(pidof print); fi
				for j in $(ls /var/spool/lpd/$i); do
					p=$(top -bn1 | grep $j | grep -v grep | cut -f2 -d" ")
					if test -n "$p"; then kill $p; fi	
					rm -f /var/spool/lpd/$i/$j >& /dev/null
				done
				rmdir /var/spool/lpd/$i/.lockdir >& /dev/null
			elif test -f /usr/bin/lprm; then
				lprm -P $i - >& /dev/null
			fi
		done
		;;

	UpdateList)
		res=$(fixup download)
		if test $? != 0; then msg "$res"; fi
		;;

	Details)
		if test "$fixaction" != "Select+one"; then
			msg "$(fixup status $fixaction)"
		else
			html_header "Fixes details"
			echo "<ul>"
			fixup list | while read st fx; do
				fxi=$(echo $fx | cut -d"-" -f1)
				msg=""; if test "$st" = "0"; then msg="(applied)"; fi
				echo "<li>$fx $msg</li><pre>"
				fixup status $fxi
				echo "</pre>"
			done
			echo "</ul>$(back_button)</body></html>"
			exit 0
		fi
		;;

	Apply)
		if test "$fixaction" != "Select+one"; then
			res=$(fixup apply $fixaction)
			if test $? != 0; then msg "$res"; fi
		fi
		;;

	Rollback)
		if test "$fixaction" != "Select+one"; then
			res=$(fixup rollback $fixaction)
			if test $? != 0; then msg "$res"; fi
		fi
		;;

	RemoveAll)
		res=$(fixup clean)
		if test $? != 0; then msg "$res"; fi
		;;

	StartAll) rcall start >& /dev/null ;;

	StopAll) rcall stop >& /dev/null ;;

	RestartAll) rcall restart >& /dev/null ;;

	ChangePassword)
		SECR=/etc/web-secret
		if test -z "$passwd"; then
			msg "The password can't be empty"
		fi

#		passwd="$(httpd -d $passwd)"
#		if test -n "$passwd" -a "$passwd" = "$(cat $SECR)"; then
#			rm -f $SECR
#			rm -f /tmp/cookie
		if test "$passwd" = $(cat /etc/web-secret /tmp/salt | md5sum - | cut -d" " -f1); then
			rm -f $SECR /tmp/cookie /tmp/salt
		else
			msg "Password doesn't match."
		fi
		gotopage /cgi-bin/login.cgi
		exit 0
		;;

	createNew)
		html_header
		busy_cursor_start

		BOX_PEM=/etc/ssl/certs/server.pem
		CUPS_CRT=/etc/cups/ssl/server.crt
		CUPS_KEY=/etc/cups/ssl/server.key
		VSFTP_CERT=/etc/ssl/certs/vsftpd.pem
		LIGHTY_PEM=/etc/ssl/certs/lighttpd.pem
		STUNNEL_CERT=/etc/ssl/certs/stunnel.pem

		rm -f $BOX_PEM $VSFTP_CERT $STUNNEL_CERT $LIGHTY_PEM $CUPS_CRT $CUPS_KEY

		rcsslcert start >& /dev/null

		rcvsftpd init >& /dev/null
		rcstunnel init >& /dev/null
		rclighttpd init >& /dev/null
		rccups init >& /dev/null

		busy_cursor_end
		js_gotopage /cgi-bin/sys_utils.cgi
		;;

	Theme)
		if test -n "$notop_menu" -a -n "$noside_menu"; then
			msg "You can't disable both menus."
		fi
		if test -s $CONFM; then . $CONFM; fi
		was=$SIDE_MENU
		sed -i -e '/^TOP_MENU/d' -e '/^SIDE_MENU/d' $CONFM
		if test -n "$notop_menu"; then echo 'TOP_MENU=no' >> $CONFM; fi
		if test -n "$noside_menu"; then echo 'SIDE_MENU=no' >> $CONFM; fi
		if test "$was" != "$noside_menu"; then 
			html_header
			echo "<script type="text/javascript">parent.location.reload(true)</script></body></html>"
			exit 0
		fi
		(cd $THM_DIR; ln -sf $(httpd -d "$set_thm") default.thm)
		;;

	UploadTheme)
		if ! unzip -p $upfile >& /dev/null; then err " The uploaded file can't be unziped."; fi

		tl=$(unzip -l $upfile | awk '/[0-9]{2}-..-../{print $4}')
		if test -z "$tl"; then err "Can't get file list from the uploaded file."; fi

		thm_name=$(basename $(echo "$tl" | grep \.thm) .thm)
		if test -z $thm_name; then err  "no .thm file found"; fi

		if test -f $THM_DIR/$thm_name.thm -o -d $THM_DIR/$thm_name; then err "theme \"$thm_name\" already exists."; fi

		if echo "$tl" | grep -qv "^$thm_name"; then err "all support files should be on a \"$thm_name\" folder."; fi

		if ! aufs.sh -s >& /dev/null; then err "you have to install one Alt-F package first."; fi

		aufs.sh -n
		mkdir -p /Alt-F/$THM_DIR
		aufs.sh -r

		unzip -qn $upfile -d $THM_DIR >& /dev/null
		rm -f $upfile
		;;

	DeleteTheme)
		set_thm=$(httpd -d "$set_thm")
		if test "$set_thm" = "dull.thm"; then
			msg "Can't delete default theme."
			exit 0
		fi

		thm_name=$(basename $set_thm .thm)

		if test $(readlink $THM_DIR/default.thm) = "$set_thm"; then
			(cd $THM_DIR; ln -sf dull.thm default.thm)
		fi

		rm -rf $THM_DIR/$set_thm $THM_DIR/$thm_name
		;;

	KernelLog)
		TF=$(mktemp -t)
		dmesg > $TF
		showlog $TF "KernelLog" "Kernel Log"
		rm -f $TF
		exit 0
		;;

	SystemLog)
		if ! rcsyslog status >/dev/null; then
			msg "Syslog is disabled, enable at 'System Services'"
		fi

		TF=$(mktemp -t)
		logread > $TF
		showlog $TF SystemLog "System Log"
		rm -f $TF
		exit 0
		;;

	Processes)
		TF=$(mktemp -t)
		top -bn1 | grep -v '\[.*\]' > $TF
		showlog $TF Processes "Running Processes"
		rm -f $TF
		exit 0
		;;

	SystemConf)
		df=/tmp/alt-f.log
		if ! test -f $df; then
			echo "No diagnostics file found, configure at Services->User, user" > $df
		fi
		showlog $df SystemConf "System Configuration"
		exit 0
		;;

	*)
		action=$(httpd -d "$action")
		if test -f "$action"; then
			showlog $action $action "Contents of $action"
			exit 0
		fi
esac

#enddebug
gotopage /cgi-bin/sys_utils.cgi
