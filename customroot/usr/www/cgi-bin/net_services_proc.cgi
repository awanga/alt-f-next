#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

start_stop() {
    local serv act
    serv=$1
    act=$2

    sscript=/etc/init.d/*$serv
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

srv="smb nfs ntp ddns dnsmasq inetd"
idx=1

for i in $srv; do
	serv=$(eval echo \$$i)

	if test -z "$serv" -a -x /etc/init.d/*$i; then
		start_stop $i disable
	elif test "$serv" = "enable" -a ! -x /etc/init.d/*$i; then
		start_stop $i enable
	elif test "$serv" = "StartNow"; then
		start_stop $i start
	elif test "$serv" = "StopNow"; then
		start_stop $i stop
	fi

	if test "$serv" = "Configure"; then
            gotopage /cgi-bin/${i}.cgi
	fi

	idx=$((idx+1))
done

ssrv="rsync ssh telnet ftp http printer swat"
idx=1
inetd_change=0
for i in $ssrv; do
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

	if test "$serv" = "Configure"; then
		gotopage /cgi-bin/${i}.cgi
	fi

	idx=$((idx+1))
done

if test $inetd_change = 1; then
    kill -HUP $(pidof inetd)
fi

#enddebug
gotopage /cgi-bin/net_services.cgi
