#!/bin/sh

. common.sh
check_cookie
write_header "SMART Setup"

CONFF=/etc/smartd.conf
CONFM=/etc/msmtprc
CONFO=/etc/misc.conf

when() {

wday=""
	j=1
	for i in Mon Tue Wed Thu Fri Sat Sun; do
		wday="$wday $i <input type=checkbox $(eval echo \$$1_$j) value=\"$j\" name=\"$1_$j\">"
		j=$((j+1))
	done
	echo $wday
}

if test -e $CONFO; then
	. $CONFO
fi

if test -z "$SMARTD_INTERVAL"; then
	SMARTD_INTERVAL=30
fi

if test -e $CONFF; then
	smartopts="$(cat $CONFF)"

	opts="$(getopt -o ad:S:M:o:m:n:s: -- $smartopts)" 2>/dev/null
	if test $? = 1; then echo ERROR; fi

	eval set -- "$opts"
	for i; do
		case $i in
		-a|--) shift;;
		-d|-S) shift; shift;;
		-m)  shift; if test -n "${1#*,}"; then MAILF=checked; fi; shift;;
		-M) MAILTF=checked; shift; shift;;
		-n) shift; if test "$1" = "never"; then WAKEF=checked; fi; shift;;
		-s) shift; tests="$1"; shift;;
		-o) AUTOF=checked; shift; offlineauto=$1; shift ;;
		esac		
	done

# FIXME this is a mess, parsing extended regular expression...
	eval $(echo $tests | tr -d '()' | awk '{
		split($0,a,"/")
		if (a[1] == "L") {
			printf "lhour=%02d; LTF=checked; ", substr(a[5],1,2)
			split(a[4],b,"|")
			for (i in b) {
				if (b[i] != "")
					printf "l_%d=checked; ", b[i]
			}
		}
		if (substr(a[5],4) == "L") {
			printf "lhour=%02d; LTF=checked; ", a[9]
		}
		if (a[1] == "|S" || a[1] == "S") {
			printf "shour=%02d; STF=checked; ", substr(a[5],1,2)
			split(a[4],b,"|")
			for (i in b) {
				if (b[i] != "")
					printf "s_%d=checked; ", b[i]
			}
		}
		if (substr(a[5],4) == "S") {
			printf "shour=%02d; STF=checked; ", a[9]
			split(a[8],b,"|")
			for (i in b) {
				if (b[i] != "")
					printf "s_%d=checked; ", b[i]
			}
		}
	}')
else
	LTF=checked; STF=checked;
	s_1=checked; s_2=checked; s_3=checked; s_4=checked; s_5=checked; s_6=checked
	l_7=checked;
	lhour=6; shour=6;
	WAKEF=checked;
fi

if test -e $CONFO; then
	SENDTO=$(awk -F= '/^MAILTO/{print $2}' $CONFO)
	if test -z "$SENDTO"; then NOMAILF=disabled; fi
fi

if ! test "$MAILF" = "checked"; then
	MAILTF="disabled"
fi

cat<<-EOF
	<script type="text/javascript">
    function toogle() {
		document.getElementById("mail_test").disabled = ! document.getElementById("mail_error").checked
    }
	</script>

	<form id="smartf" action="/cgi-bin/smart_proc.cgi" method="post">
	<table>
	<tr><td><input type=checkbox $STF name="shorttest" value="yes">
		Do a short disk test every: $(when s) 
		at <input type=text size=2 name=shorthour value="$shour">:00</td>
	</tr> 
	<tr><td><input type=checkbox $LTF name="longtest" value="yes">
		Do a long disk test every:&nbsp; $(when l)
		at <input type=text size=2 name=longhour value="$lhour">:00</td>
	</tr>

	<tr><td><input type=checkbox $WAKEF name="wakeup" value="yes">
	Wake up disk to perform test</td></tr>

	<tr><td><input type=checkbox $AUTOF name="offlineauto" value="yes">
	Scans the drive every four hours for disk defects</td></tr>

	<tr><td><br>Send mail to <input type=text readonly name=sendto value="$SENDTO">
	Use "Setup Mail" to change</td></tr>

	<tr><td><input type=checkbox id="mail_error" $MAILF $NOMAILF name="mailerror" value="yes" onclick="toogle()">
	Send e-mail when an error is detected</td></tr>

	<tr><td><input type=checkbox id="mail_test" $MAILTF $NOMAILF name="mailtest" value="yes">
	Send test e-mail when started</td></tr>

	<tr><td><br>Check disks every <input type=text name=interval size=4 value="$SMARTD_INTERVAL">
	minutes</td></tr>
	</table>
	<p><input type="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
