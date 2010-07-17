#!/bin/sh

. common.sh
check_cookie
read_args

#debug

# the user can hit the enter key instead of pressing the button
if test -n "$passwd"; then
	action="ChangePassword"

elif test "$kernel" = "Refresh"; then
	action="KernelLog"

elif test "$syslog" = "Refresh"; then
	action="SystemLog"

elif test "$kernel" = "Back" -o "$syslog" = "Back"; then
	gotopage /cgi-bin/system.cgi
fi

case $action in
	Reboot)
		/sbin/reboot
		;;
	
	Poweroff) 
		/sbin/poweroff
		;;

	ClearPrintQueues)
		#lpq -d doesnt work
		for i in $(cut -f1 -d"|" /etc/printcap ); do
			if test -d /var/spool/lpd/$i; then
				mkdir -p /var/spool/lpd/$i/.lockdir  # see /usr/bin/print
				if test -n "$(pidof print)"; then kill $(pidof print); fi
				for j in $(ls /var/spool/lpd/$i); do
					p=$(top -n1 | grep $j | grep -v grep | cut -f2 -d" ")
					if test -n "$p"; then
						kill $p
					fi	
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
		echo "<pre>"
		dmesg
		cat<<-EOF
			</pre>
			<form action="/cgi-bin/system_proc.cgi" method="post">
			<input type=submit name=kernel value="Refresh">
			<input type=submit name=kernel value="Back">
			</form></body></html>
		EOF
		exit 0
		;;

	SystemLog)
		write_header "System Log"
		if ! rcsyslog status >/dev/null; then
			echo "Syslog is disabled, enable at \"System Services\""
		else
			echo "<pre>"
			logread
			echo "</pre>"
		fi
		cat<<-EOF
			<form action="/cgi-bin/system_proc.cgi" method="post">
			<input type=submit name=syslog value="Refresh">
			<input type=submit name=syslog value="Back">
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


	*)
		echo Hu? ;;

esac

#enddebug

gotopage /cgi-bin/system.cgi


