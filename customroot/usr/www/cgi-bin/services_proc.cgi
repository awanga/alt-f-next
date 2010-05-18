#!/bin/sh

# start_stop service action
start_stop() {
	local serv act
	serv=$1
	act=$2

	sscript=/etc/init.d/S??$serv
	if test -n "$sscript"; then    
		if test "$act" = "enable"; then
			chmod +x $sscript
			$sscript start >/dev/null 2>&1
		elif test "$act" = "disable"; then
			$sscript stop >/dev/null 2>&1
			chmod -x $sscript
		elif test "$act" = "start"; then
			sh $sscript start >/dev/null 2>&1
			sleep 1
		elif test "$act" = "stop"; then
			sh $sscript stop >/dev/null 2>&1
			sleep 1
		fi
	fi
}

. common.sh
read_args
check_cookie

#debug

if test -n "$Submit"; then

	srvs="$(httpd -d $Submit)"
	for i in $srvs; do
		st=$(eval echo \$$i)
		if test "$st" = "enable" -a ! -x /etc/init.d/S??$i; then
			start_stop $i enable
		elif test "$st" != "enable" -a -x /etc/init.d/S??$i; then
			start_stop $i disable
		fi
	done

elif test -n "$StartNow"; then
	start_stop $StartNow start

elif test -n "$StopNow"; then
	start_stop $StopNow stop

elif test -n "$StartAll"; then
	rcall start >& /dev/null

elif test -n "$StopAll"; then
	rcall stop >& /dev/null

elif test -n "$RestartAll"; then
	rcall restart >& /dev/null

elif test -n "$Configure"; then
	if test -f $PWD/${Configure}.cgi; then
		gotopage /cgi-bin/${Configure}.cgi
	else
		write_header "$Configure setup"
		echo "<p>Write me</p>"
		back_button
		echo "</body></html>"
		exit 0
	fi
fi

#enddebug

back=$(echo $HTTP_REFERER | sed -n 's|.*/cgi-bin/||p')
gotopage /cgi-bin/$back
