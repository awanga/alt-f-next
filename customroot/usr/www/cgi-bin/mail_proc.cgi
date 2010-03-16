#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/msmtprc

user=$(httpd -d "$user")
to=$(httpd -d "$to")

if test -z "$tls"; then tls=off; fi
if test -z "$auth"; then auth=on; fi

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
if test -n "$password"; then echo -e "password\t$password" >> $CONFF; fi
if test -n "$to"; then echo -e "from\t$to" >> $CONFF; fi

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

