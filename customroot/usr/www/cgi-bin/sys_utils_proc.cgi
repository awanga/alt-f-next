#!/bin/sh

. common.sh
check_cookie
read_args

CONFM=/etc/misc.conf
    
#debug

# the user can hit the enter key instead of pressing the button
if test -n "$passwd"; then
	action="ChangePassword"

elif test "$kernel" = "Refresh"; then
	action="KernelLog"

elif test "$syslog" = "Refresh"; then
	action="SystemLog"
fi

case $action in
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
		/sbin/poweroff
		;;

	ClearPrintQueues)
		#lpq -d doesnt work
		for i in $(cut -f1 -d"|" /etc/printcap 2>/dev/null); do
			if test -d /var/spool/lpd/$i; then
				mkdir -p /var/spool/lpd/$i/.lockdir  # see /usr/bin/print
				if test -n "$(pidof print)"; then kill $(pidof print); fi
				for j in $(ls /var/spool/lpd/$i); do
					p=$(top -n1 | grep $j | grep -v grep | cut -f2 -d" ")
					if test -n "$p"; then kill $p; fi	
					rm /var/spool/lpd/$i/$j
				done
				rmdir /var/spool/lpd/$i/.lockdir
			elif test -f /usr/bin/lprm; then
				lprm -P $i - >& /dev/null
			fi
		done
		;;

	KernelLog)
		write_header "Kernel Log"
		echo "<small><pre>"
		dmesg
		cat<<-EOF
			</small></pre>
			<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
			<input type=submit name=kernel value="Refresh">
			$(back_button)
			</form></body></html>
		EOF
		exit 0
		;;

	SystemLog)
		write_header "System Log"
		if ! rcsyslog status >/dev/null; then
			echo "Syslog is disabled, enable at \"System Services\""
		else
			echo "<pre><small>"
			logread
			echo "</small></pre>"
		fi
		cat<<-EOF
			<form action="/cgi-bin/sys_utils_proc.cgi" method="post">
			<input type=submit name=syslog value="Refresh">
			$(back_button)
			</form></body></html>
		EOF
		exit 0
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
		if test "$passwd" = $(cat $SECR); then
			rm -f $SECR
			rm -f /tmp/cookie
		fi
		gotopage /cgi-bin/login.cgi
		exit 0
		;;
esac

#enddebug

gotopage /cgi-bin/sys_utils.cgi


