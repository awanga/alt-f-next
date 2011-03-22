#!/bin/sh

. common.sh
check_cookie
read_args

CONFM=/etc/misc.conf
    
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

	write_header "$3"
	mktt filter_tt "Enter a search string (or a grep regular expression)"

	echo "<small><pre>"

	if test -n "$filter_str"; then
		pat=$(httpd -d $filter_str)
		cat $1 | grep -i "$pat"
	else
		cat $1
	fi

	cat<<-EOF
		</small></pre>
		<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
		$(back_button)
		<input type=submit name=$1 value="Download">
		Filter: <input type=text name=filter_str value="$pat" onkeypress="return event.keyCode != 13" $(ttip filter_tt)>
		<input type=submit name=$2 value="Refresh">
		<input type=hidden name=logfile value="$2">
		</form></body></html>
	EOF
}

if test -n "$Refresh"; then
	action="$Refresh"
elif test -n "$Download"; then
	action="$logfile"
elif test -n "$logaction" -a "$logaction" != "Select+one"; then
	action="$logaction"
fi

case "$action" in
	Reboot)
		html_header
		cat<<-EOF
			<br><br><fieldset><legend><strong>The box is rebooting</strong></legend>
			<center><h4>
			$(wait_count_start "Waiting 45 seconds")
			</h4></center></fieldset>
			<script type=text/javascript>
				setTimeout('window.location.assign("http://" + location.hostname + "/cgi-bin/status.cgi")', 45000)
			</script></body></html>
		EOF
		/sbin/reboot
		exit 0
		;;
	
	Poweroff)
		html_header
		echo "<br><br><strong><center>The box is being powered off.</center></strong></body></html>"
		/sbin/poweroff
		exit 0
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

	StartAll)
		rcall start >& /dev/null
		;;

	StopAll)
		rcall stop >& /dev/null
		;;

	RestartAll)
		rcall restart >& /dev/null
		;;

	ChangePassword)
		SECR=/etc/web-secret
		if test -n "$passwd" -a "$passwd" = $(cat $SECR); then
			rm -f $SECR
			rm -f /tmp/cookie
		else
			msg "Password doesn't match."
		fi
		gotopage /cgi-bin/login.cgi
		exit 0
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
		top -bn1 > $TF
		showlog $TF Processes "Running Processes"
		rm -f $TF
		exit 0
		;;

	*)
		act=$(httpd -d $action)
		if test -f "$act"; then
			showlog $act $act "Contents of $act"
			exit 0
		fi
esac

#enddebug
gotopage /cgi-bin/sys_utils.cgi
