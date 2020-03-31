#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

read_args
check_cookie

#debug

CONFF=/etc/inadyn.conf
SCACHE=/var/cache/ddns

sites="dyndns@dyndns.org default@zoneedit.com default@no-ip.com default@freedns.afraid.org
default@easydns.com dyndns@3322.org default@sitelutions.com default@dnsomatic.com ipv6tb@he.net
default@tzo.com default@dynsip.org default@dhis.org default@majimoto.net default@zerigo.com default@two-dns.de default@dnsdynamic.org default@dnspark.com ipv4@regfish.de ipv6@regfish.de default@ovh.com default@joker.com default@strato.com default@system-ns.com default@dtdns.com default@changeip.com default@dnsexit.com ipv4@nsupdate.info ipv6@nsupdate.info default@loopia.com default@duckdns.org default@dy.fi"

provider=$(httpd -d "$provider")

for i in $sites; do
	site=$(echo $i | cut -d"@" -f2)
	if test "$provider" = "$site"; then ddns=$i; fi
done

passwd=$(checkpass "$passwd")
if test $? != 0; then
	msg "$passwd"
fi

if test -n "$ipsn"; then
	ipsn=$(httpd -d "$ipsn")
else
	ipsn="checkip.dyndns.org /"
fi

if test -n "$ddns" -a -n "$host"; then
	host=$(httpd -d "$host")
	llevel=3
	if test "$verbose" = "yes"; then llevel=5; fi

	cat<<-EOF > $CONFF
		dyndns_system $ddns
		alias $host
		username $user
		password $passwd
		ip_server_name $ipsn
		verbose $llevel
		cache_dir $SCACHE
		update_period_sec 600
		syslog
		lang_file
	EOF
	chmod og-rw $CONFF
fi

if rcddns status >& /dev/null; then
	rcddns restart >& /dev/null
fi	

#enddebug
gotopage /cgi-bin/net_services.cgi
