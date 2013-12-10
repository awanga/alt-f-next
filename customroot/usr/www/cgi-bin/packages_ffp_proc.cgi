#!/bin/sh

# $1: funpkg arg (-i|-u) $2: package
download() {

	if ! nslookup $RSITE >& /dev/null; then
		msg "You don't seem to have a name server configured, or a working internet connection."
	fi

	write_header "Installing ffp package $2" 

	pname=$2.$arch_ext

	echo "<pre>"
	wget --tries=3 --progress=dot:mega $FSITE/$FDIR/$FFP_DIR/packages/$pname \
		-O $TMPDIR/$pname
	if test $? != 0; then
		wget --tries=3 --progress=dot:mega $xtra_pkgs/$pname \
			-O $TMPDIR/$pname
	fi
	st=$?

	if test $st = 0; then
		PATH=/ffp/bin:/ffp/sbin:$PATH funpkg $1 $TMPDIR/$pname
		st=$?
	fi

	rm -f $TMPDIR/$pname
	if test $st = 0; then
		echo "</pre><p><strong>Success</strong></p>"
		goto_button Continue /cgi-bin/packages_ffp.cgi
	else
		echo "</pre><p><strong>Error</strong></p>"
		goto_button Back /cgi-bin/packages_ffp.cgi
	fi
	echo "</body></html>"
	exit 0
}

. common.sh
check_cookie
read_args

#debug

RSITE=www.inreto.de
FSITE="http://$RSITE"
FDIR="dns323/fun-plug"

if test "$ffpver" = "0.5"; then
	FFP_DIR="0.5"
	arch_ext=tgz
	xtra_pkgs="$FSITE/$FDIR/0.5/extra-packages/All/"
elif test "$ffpver" = "0.7"; then
	FFP_DIR="0.7/oabi"
	bbext="-netutils"
	arch_ext=txz
	xtra_pkgs="$FSITE/$FDIR/0.7/oabi/extras/"
else
	msg "Incorrect ffp version"
fi

TMPDIR=/ffp/tmp
PATH=$PATH:/ffp/bin:/ffp/sbin 

if test "$install" = "Install"; then
	if test "$part" = "none"; then
		msg "You must select a filesystem. A folder named 'ffp' will be created there."
	fi

	if ! nslookup $RSITE >& /dev/null; then
		msg "You don't seem to have a name server configured, or a working internet connection."
	fi

	part=$(httpd -d $part)
	mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)
	ffpdir=$mp/ffp

	if test -d $ffpdir; then
		effp=$ffpdir
	elif test -d $ffpdir-$ffpver; then
		effp=$ffpdir-$ffpver
	fi

	if test -n "$effp" -a -f $effp/etc/ffp-version; then
		mv $effp $ffpdir >& /dev/null
		ln -sf $ffpdir /ffp
		. /ffp/etc/ffp-version
		msg "A ffp-$FFP_VERSION installation was found in $part and reused."
	fi

	TMPF=/tmp/fun_plug.tgz
	SITE=$FSITE/$FDIR/$FFP_DIR/fun_plug.tgz
#test	SITE=http://flash/~jcard/fun_plug-$ffpver.tgz

	write_header "Installing FFP-$ffpver"

	echo "<p><strong>Downloading...</strong></p><pre>"
	wget --tries=3 --progress=dot:mega $SITE -O $TMPF
	st=$?
	echo "</pre>"

	if test $st = 0; then
		echo "<p><strong>Installing... "

		mkdir -p $ffpdir
		tar -C $ffpdir -xzf $TMPF

		if test $? = 0; then
			ln -sf $ffpdir /ffp
			if test "$ffpver" = "0.5"; then
				echo FFP_VERSION=0.5 > /ffp/etc/ffp-version
			fi
			chown root.root /ffp/bin/busybox$bbext
			chmod 0755 /ffp/bin/busybox$bbext
			chmod u+s /ffp/bin/busybox$bbext
			chmod -x /ffp/start/*
			echo "success.</strong></p>"
			st=0
		else
			echo "fail.</strong></p>"
			st=1
		fi
	else
		echo "<p><strong>Download failed.</strong></p>"
		st=1
	fi
	rm -f $TMPF

	if test $st = 0; then
		goto_button Continue /cgi-bin/packages_ffp.cgi
	else
		goto_button Back /cgi-bin/packages_ffp.cgi
	fi
	echo "</body></html>"
	exit 0

elif test -n "$Remove"; then
	PATH=/ffp/bin:/ffp/sbin:$PATH funpkg -r $Remove >& /dev/null

elif test -n "$Install"; then
	download -i $Install

elif test -n "$Update"; then
	download -u $Update

elif test -n "$Uninstall"; then
	rm -rf $(readlink -f /ffp) /ffp

elif test -n "$Upgrade"; then
	ffpdir=$(dirname $(readlink -f /ffp))
	mv "$ffpdir"/ffp "$ffpdir"/ffp-0.5
	if test -d "$ffpdir"/ffp-0.7; then
		mv "$ffpdir"/ffp-0.7 "$ffpdir"/ffp
		ln -sf "$ffpdir"/ffp /ffp
	else
		rm /ffp
	fi

elif test -n "$Downgrade"; then
	ffpdir=$(dirname $(readlink -f /ffp))
	mv "$ffpdir"/ffp "$ffpdir"/ffp-0.7
	if test -d "$ffpdir"/ffp-0.5; then
		mv "$ffpdir"/ffp-0.5 "$ffpdir"/ffp
		ln -sf "$ffpdir"/ffp /ffp
	else
		rm /ffp
	fi
fi

#enddebug
#exit 0

gotopage /cgi-bin/packages_ffp.cgi
