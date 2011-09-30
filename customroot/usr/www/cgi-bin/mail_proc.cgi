#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/msmtprc

if test -z "$tls"; then tls=off; fi
if test -z "$auth"; then auth=on; fi

if test -z "$to"; then
	msg "Send To entry must be filled"
fi

if test -z "$host"; then
	msg "Server Name must be filled"
fi

if test "$auth" = "on" -a \( -z "$user" -o -z "$password" \); then
	msg "Username and Password must be filled"
fi

password=$(checkpass $password)
if test $? != 0; then
    msg "$password"
fi

user=$(httpd -d "$user")
to=$(httpd -d "$to")

#debug

echo "
tls_trust_file	/etc/ssl/ca-bundle.crt
syslog		on
auto_from	on
host	$host
tls		$tls
auth	$auth" > $CONFF

if test -n "$port"; then echo -e "port\t$port" >> $CONFF; fi
if test -n "$user"; then echo -e "user\t$user" >> $CONFF; fi
if test -n "$to"; then echo -e "from\t$to" >> $CONFF; fi
if test -n "$password"; then echo -e "password\t$password" >> $CONFF; fi

chmod 600 $CONFF

if test "$submit" = "Test"; then
	msmtp --read-recipients<<-EOF
		To: $to
		Subject: DNS-323 ALT-F mail test
		
		This is a test message
	EOF
	if test $? = 0; then
		msg "Mail sent."
	else
		msg "Sent mail failed: $(logread | grep msmtp | tail -1)"
	fi
fi

#enddebug
gotopage /cgi-bin/mail.cgi

