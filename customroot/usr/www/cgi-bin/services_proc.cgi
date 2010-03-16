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
		elif test "$act" = "stop"; then
			sh $sscript stop >/dev/null 2>&1
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

	if test -n "$SSubmit"; then # inetd services 
		ssrvs="$(httpd -d $SSubmit)"
		for i in $ssrvs; do
			serv=$(eval echo \$$i)
			grep -q -e "^$i" /etc/inetd.conf
			st=$?

			if test -z "$serv" -a "$st" = "0"; then
				inetd_change=1
				sed -i s/$i/#$i/ /etc/inetd.conf
			elif test "$serv" = "enable" -a "$st" != "0"; then
				inetd_change=1
				sed -i s/#$i/$i/ /etc/inetd.conf
			fi
		done
		if test "$inetd_change" = 1; then
    		kill -HUP $(pidof inetd)
		fi
	fi

elif test -n "$StartNow"; then
	start_stop $StartNow start

elif test -n "$StopNow"; then
	start_stop $StopNow stop

elif test -n "$Configure"; then
	gotopage /cgi-bin/${Configure}.cgi
fi

#enddebug

back=$(echo $HTTP_REFERER | sed -n 's|.*/cgi-bin/||p')

gotopage /cgi-bin/$back
