#!/bin/sh

# start_stop service action
start_stop() {
	local serv act
	serv=$1
	act=$2

	sscript=/etc/init.d/S??$serv
	rcscript=rc${serv}
	if test -n "$sscript"; then
		busy_cursor_start
		if test "$act" = "enable"; then
			$rcscript enable >& /dev/null
		elif test "$act" = "disable" -a "$rcscript" != "rcinetd"; then
			$rcscript disable >& /dev/null
		fi

		if test "$act" = "start" -o "$act" = "enable"; then
			if ! res=$($rcscript start 2>&1); then
				msg "$res"
			fi
		elif test "$act" = "stop" -o "$act" = "disable"; then
			if ! res=$($rcscript stop 2>&1); then
				msg "$res"
			fi
			for i in $(seq 1 50); do
				if ! $rcscript status >& /dev/null; then
					break
				fi	
				usleep 200000
			done
			if test "$i" -eq 50; then
				msg "Service was signaled to stop but it is slow to react, please wait."
			fi
		fi
		busy_cursor_end
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

elif test -n "$Configure"; then
	gotopage /cgi-bin/${Configure}.cgi
fi

#enddebug

back=$(echo $HTTP_REFERER | sed -n 's|.*/cgi-bin/||p')
js_gotopage /cgi-bin/$back
