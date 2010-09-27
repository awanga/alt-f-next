#!/bin/sh

jsback() {
	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
	EOF
}

download() {
	nm=${2%%.tgz}
	write_header "Installing ffp package $nm" 
	jsback

	echo "<pre>"
	wget --tries=3 --progress=dot:mega \
		http://www.inreto.de/dns323/fun-plug/0.5/packages/$2 \
		-O $TMPDIR/$2
	if test $? = 1; then
		wget --tries=3 --progress=dot:mega  \
			http://www.inreto.de/dns323/fun-plug/0.5/extra-packages/All/$2 \
			-O $TMPDIR/$2
	fi
	st=$?

	if test $st = 0; then
		funpkg $1 $TMPDIR/$2
		st=$?
	fi
	
	rm -f $TMPDIR/$2
	if test $st = 0; then
		cat<<-EOF
			</pre><p> <strong> Success </strong> </p>
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	else
		cat<<-EOF
			</pre><p> <strong> Error </strong> </p>
			<input type="button" value="Back" onclick="err()"></p>
		EOF
	fi
	echo "</body></html>"
	exit 0
}

. common.sh
check_cookie
read_args

#debug

TMPDIR=/ffp/tmp

# this script needs thi, as funpkg doesn't set its own PATH
PATH=$PATH:/ffp/bin:/ffp/sbin 

if test "$install" = "Install"; then
	if test "$part" = "none"; then
		msg "You must select a partition"
	fi

	if ! nslookup www.inreto.de >& /dev/null; then
		msg "You don't seem to have a name server configured, or a working internet connection."
	fi

	TMPF=/tmp/fun_plug.tgz
	SITE=http://www.inreto.de/dns323/fun-plug/0.5/fun_plug.tgz
	#SITE=http://silver/~jcard/fun_plug.tgz

	write_header "Installing FFP"
	jsback

	echo "<p><strong> Downloading... </strong> </p><pre>"
	wget --tries=3 --progress=dot:mega  $SITE -O $TMPF #\ 
		# 2>&1 | sed -nu -e 's/^ *=>.*//' -e 's/^ //p'
	st=$?
	echo "</pre>"

	if test $st = 0; then
		echo "<p> <strong> Installing... "
		part=$(httpd -d $part)
		mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)
		mkdir -p $mp/ffp
		tar -C $mp/ffp -xzf $TMPF

		if test $? = 0; then
			ln -sf $mp/ffp /ffp
			chown root.root /ffp/bin/busybox
			chmod 0755 /ffp/bin/busybox
			chmod u+s /ffp/bin/busybox
			chmod -x /ffp/start/*
			echo " success. </strong> </p>"
			st=0
		else
			echo " fail. </strong> </p>"
			st=1
		fi
	else
		echo "<p> <strong> Download failed. </strong> </p>"
		st=1
	fi
	rm -f $TMPF

	if test $st = 0; then
		cat<<-EOF
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	else
		cat<<-EOF
			<input type="button" value="Back" onclick="err()">
		EOF
	fi
	echo "</body></html>"
	exit 0

elif test -n "$Remove"; then
	funpkg -r $Remove >& /dev/null

elif test -n "$Install"; then
	download -i $Install.tgz

elif test -n "$Update"; then
	download -u $Update.tgz

elif test -n "$Uninstall"; then
	rm -rf $(readlink -f /ffp) /ffp
fi

gotopage /cgi-bin/packages_ffp.cgi
