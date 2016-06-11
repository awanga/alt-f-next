#!/bin/sh

. common.sh
read_args
check_cookie

CONFF=/etc/inetd.conf

#debug
#set -x 

if test -n "$Configure"; then
	gotopage /cgi-bin/${Configure}.cgi

elif test -n "$Submit"; then

	cnt=$(eval echo \$cnt)
	for i in $(seq 1 $cnt); do
		chk=$(eval echo \$chk_$i)
		srv=$(eval echo \$srv_$i)
		prog=$(eval echo \$prog_$i)
		script=""
		if test -f /sbin/rc$prog; then
			script=$(echo /etc/init.d/S??$prog) # hack: pathname expansion
		fi

		if test "$chk" = "enable"; then
			to_enable="$to_enable $srv"
			if test -f "$script"; then
				rc$prog stop >& /dev/null
				#sed -i 's/^TYPE=/#TYPE=/' $script
			fi
		else
			to_disable="$to_disable $srv"
			#if test -f "$script"; then
			#	sed -i 's/^#TYPE=/TYPE=/' $script
			#fi
		fi
	done

	if test -n "$to_enable"; then rcinetd enable $to_enable >& /dev/null; fi
	if test -n "$to_disable"; then rcinetd disable $to_disable >& /dev/null; fi

# normalize corner cases:
# 1-stunnel controls swats *and* https,this is handled by the iniscript,
# although inconsistent entries appears in the inetd page
# 2-vsftpd controls ftp *and/or* ftps. WHAT TO DO?
# the initscrip starts tow daemons. does this makes sense? Shouldnt both servers be only available through inetd or standalone? This would solve the initscript inconsistent output -- both server should be running to get the proper status; and it would simplify the webUI, as having two inetd/server for ftp/ftps choices does not seems OK.

	#enddebug
	gotopage /cgi-bin/net_services.cgi
fi
