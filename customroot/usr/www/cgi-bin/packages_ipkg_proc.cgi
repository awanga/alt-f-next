#!/bin/sh

. common.sh
check_cookie
read_args

CONFF=/etc/ipkg.conf

# FIXME: When updating packages with libraries, if the library is in use by some program
# the update/upgrade might fail without notice.
# The fast cure is to always stop all services before updating or upgrading packages.

#debug
#set -x

change_feeds() {
	mv $CONFF $CONFF-
	for i in $(seq 1 $nfeeds); do
		eval $(echo feed=\$feed_$i)
		if test -z "$feed"; then continue; fi
		feed=$(httpd -d "$feed")
		eval $(echo cmt=\$dis_$i)
		if test -n "$cmt"; then cmt="#!#"; fi
		echo "${cmt}src feed_$i $feed" >> $CONFF
	done
	echo "dest /Alt-F /Alt-F" >> $CONFF
}

ipkg_cmd() {
	if test $1 = "-install"; then
		write_header "Installing Alt-F"
	elif test $1 = "install"; then
		write_header "Installing Alt-F package $2"
		opts="-force-defaults"
	elif test $1 = "upgrade"; then
		write_header "Upgrading all Alt-F packages"
		opts="-force-defaults"
	fi

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
	EOF

	echo "<pre>"

	ipkg $opts $1 $2
	if test $? = 0; then
		cat<<-EOF
			</pre>
			<p><strong>Success</strong>
			<script type="text/javascript">
				setTimeout("err()", 2000);
			</script>
		EOF
	else
		if test $1 = "-install"; then
			ipkg -clean
		fi

		cat<<-EOF
			</pre>
			<p><strong>An error occurred </strong>
			<input type="button" value="Back" onclick="err()"></p>
		EOF
	fi
	echo "</body></html>"
	exit 0
}

if test "$install" = "Install"; then
	if test "$part" = "none"; then
		msg "You must select a filesystem first."
	fi

	part=$(httpd -d $part)
	mp=$(cat /proc/mounts | grep $part | cut -d" " -f2)

	change_feeds

	ipkg_cmd -install $mp

elif test -n "$BootEnable"; then
	aufs.sh -n
	for i in $(seq 1 $ninstall); do
		af=$(eval echo \$altf_dir_$i)
		af=$(httpd -d "$af")
		touch $af/NOAUFS
		if test -n "$(eval echo \$BootEnable_$i)"; then
			rm -f $af/NOAUFS
		fi
	done
	aufs.sh -r
	gotopage /cgi-bin/packages_ipkg.cgi

elif test -n "$Delete"; then
	# FIXME: this does not remove package files installed elsewhere, e.g. /opt,
	# and we can't use 'ipkg -clean'
	altf_dir=$(httpd -d "$Delete")
	curr_altf=$(realpath /Alt-F 2> /dev/null)
	busy_cursor_start
	if test "$curr_altf" = "$altf_dir"; then
		if ! hot_aux.sh -stop-altf-dir "$curr_altf"; then
			busy_cursor_end
			msg "Current \"$curr_altf\" folder couldn't be deactivated to be deleted"
		fi
	fi
	if mountpoint -q "$(dirname $altf_dir)" && test "$(basename $altf_dir)" = "Alt-F"; then
		rm -rf "$altf_dir"
	fi
	busy_cursor_end
	js_gotopage /cgi-bin/packages_ipkg.cgi

elif test -n "$ActivateNow"; then
	busy_cursor_start
	if curr_altf=$(realpath /Alt-F 2> /dev/null); then
		if ! hot_aux.sh -stop-altf-dir "$curr_altf"; then
			busy_cursor_end
			msg "Current \"$curr_altf\" folder couldn't be deactivated"
		fi
	fi
	altf_dir=$(httpd -d "$ActivateNow")
	rm -f "$altf_dir/NOAUFS"
	hot_aux.sh -start-altf-dir "$altf_dir"
	busy_cursor_end
	js_gotopage /cgi-bin/packages_ipkg.cgi

elif test -n "$DeactivateNow"; then
	altf_dir=$(httpd -d "$DeactivateNow")
	busy_cursor_start
	if ! hot_aux.sh -stop-altf-dir "$altf_dir"; then
		busy_cursor_end
		msg "Current \"$altf_dir\" folder couldn't be deactivated"
	fi
	busy_cursor_end
	js_gotopage /cgi-bin/packages_ipkg.cgi

elif test -n "$CopyTo"; then
	idx=$CopyTo
	part=$(eval echo \$part$idx)
	part=$(httpd -d "$part")
	if test "$part" = "none"; then
		msg "You must select a filesystem"
	fi

	if ! blkid $(cat /proc/mounts | grep $part | cut -d" " -f1) | grep -qE 'ext(2|3|4)'; then
		msg "The destination has to be a linux ext2/3/4 filesystem"
	fi

	dest=$(cat /proc/mounts | grep $part | cut -d" " -f2)
	if test -d "$dest/Alt-F"; then
		msg "The destination  already has an Alt-F folder"
	fi

	altf_dir=$(eval echo \$altf_dir_$idx)
	altf_dir=$(httpd -d "$altf_dir")

	if test "$(dirname $altf_dir)" = "$dest"; then
		msg "The source and destinations are the same"
	fi

	busy_cursor_start
	cp -a $altf_dir $dest >& /dev/null
	busy_cursor_end
	js_gotopage /cgi-bin/packages_ipkg.cgi

elif test -n "$Submit"; then
	change_feeds
fi

res=$(ipkg update)

if test $? != 0; then
	msg "$res"
fi

if test -n "$Remove"; then
	res=$(ipkg remove $Remove 2>&1 | sed -n '/^Package/,/^$/p')

	if test -n "$res"; then
		msg "$res"
	fi

elif test -n "$InstallAll"; then
	write_header "Installing all Alt-F packages"
	echo "<pre>"
	for i in $(ipkg -V0 list | cut -f1 -d" "); do
		if ! ipkg -V0 list_installed | cut -f1 -d" " | grep -q $i; then
			ipkg install $i
		fi
	done 
	cat<<-EOF
		</pre>
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
			setTimeout("err()", 2000);
		</script>
		</body></html>
	EOF
	exit 0

elif test -n "$Install"; then
	ipkg_cmd install $Install

elif test -n "$Update"; then
	ipkg_cmd install $Update

elif test -n "$UpdateAll"; then
	ipkg_cmd upgrade
fi

#enddebug
gotopage /cgi-bin/packages_ipkg.cgi



