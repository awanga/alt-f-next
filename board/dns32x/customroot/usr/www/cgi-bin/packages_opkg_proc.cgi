#!/bin/sh

. common.sh
check_cookie
read_args

#debug
#set -x

PATH=$PATH:/opt/bin:/opt/sbin
CONFF=/opt/etc/opkg.conf

opkg_cmd() {
	opt=$1
	if test $1 = "install"; then
		write_header "Installing Entware package $2"
	elif test $1 = "remove"; then
		write_header "Removing Entware package $2"
		opt="--autoremove $opt"
	elif test $1 = "upgrade"; then
		write_header "Upgrading all Entware packages"
	elif test $1 = "update"; then
		write_header "Updating Entware packages list"
	fi

	cat<<-EOF
		<script type="text/javascript">
			function err() {
				window.location.assign(document.referrer)
			}
		</script>
	EOF

	busy_cursor_start
	echo "<pre>"
	opkg $opt $2				
	if test $? = 0; then
		cat<<-EOF
			</pre>
			<p><strong>Success</strong>
			<input type="button" value="Continue" onclick="err()"></p>
			<!--script type="text/javascript">
				setTimeout("err()", 2000);
			</script-->
		EOF
	else
		cat<<-EOF
			</pre>
			<p><strong>An error occurred </strong>
			<input type="button" value="Back" onclick="err()"></p>
		EOF
	fi
	busy_cursor_end
	echo "</body></html>"
	exit 0
}

if test "$install" = "Install"; then
	if false; then # FIXME: this should be the normal beaviour
		if test "$part" = "none"; then
			msg "You must select a filesystem first."
		fi

		part=$(httpd -d $part)
		mkdir /mnt/$part/opt
		ln -sf /mnt/$part/opt /opt
	else
		mkdir -p /opt # creates /Alt-F/opt, which appears as /opt
	fi
	
	write_header "Installing Entware"
	busy_cursor_start

	feed=$(httpd -d $feed_1)
	echo "<p><strong>Downloading...</strong></p><pre>"
	if ! wget $feed/installer/generic.sh -O /tmp/generic.sh; then
		echo "</pre><p><strong>Downloading the installer from $feed failed.</strong></p>"
		rm -f /tmp/generic.sh
		err=1
	else
		echo "</pre><p><strong>Installing...</strong></p><pre>"
		if ! sh /tmp/generic.sh; then
			echo "</pre><p><strong>Executing the installer failed.</strong></p>"
			err=1
		fi
	fi

	busy_cursor_end

	if test -z "$err"; then
		if ! test -d /Alt-F/etc/init.d; then
			aufs.sh -n
			mkdir -p /Alt-F/etc/init.d # fix, a defective install might exists
			aufs.sh -r
		fi
		cat<<-EOF  >/etc/init.d/S81entware
			#!/bin/sh

			DESC="Software repository for network attached storages, routers and other embedded devices."
			TYPE=user

			. /etc/init.d/common

			if ! test -f /opt/etc/init.d/rc.unslung; then
				echo "No Entware installation found."
				exit 1    
			fi
 
			export PATH=/opt/bin:/opt/sbin:\$PATH

			case "\$1" in
					start) /opt/etc/init.d/rc.unslung start ;;
					stop) /opt/etc/init.d/rc.unslung stop ;;
					status) /opt/etc/init.d/rc.unslung check ;;
					restart) /opt/etc/init.d/rc.unslung restart ;;
					*)  usage \$0 "start|stop|status|restart" ;;
			esac
		EOF
		ln -sf /usr/sbin/rcscript /sbin/rcentware
	fi

	cat<<-EOF
		</pre>
		<script type="text/javascript">
		</script>
		<input type="button" value="Continue" onclick="window.location.assign(document.referrer)"></p>
		</body></html>
	EOF
	exit 0

elif test -n "$RemoveAll"; then
	write_header "Removing Entware"
	echo "<pre>"
	busy_cursor_start
	rcentware stop >& /dev/null
	for i in bin etc lib sbin share tmp usr var; do
		rm -rf /opt/$i
	done
	busy_cursor_end
	echo "</pre>"
	rm -f /etc/init.d/S81entware /sbin/rcentware
	js_gotopage /cgi-bin/packages_opkg.cgi

elif test "$Submit" = "changeFeeds"; then
	sed -i '\|src/gz|d' $CONFF
	for i in $(seq 1 $nfeeds); do
		eval $(echo feed=\$feed_$i)
		if test -z "$feed"; then continue; fi
		feed=$(httpd -d "$feed")
		eval $(echo cmt=\$dis_$i)
		if test -n "$cmt"; then cmt="#!#"; fi
		echo "${cmt}src/gz feed_$i $feed" >> $CONFF
	done
	opkg_cmd update

elif test -n "$UpdatePackageList"; then
	opkg_cmd update

elif test -n "$Remove"; then
	opkg_cmd remove $Remove

elif test -n "$Install"; then
	opkg_cmd install $Install

elif test -n "$Update"; then
	opkg_cmd install $Update

elif test -n "$UpdateAll"; then
	opkg_cmd upgrade

elif test -n "$search"; then
	gotopage "/cgi-bin/packages_opkg.cgi?search=$search"
fi

#enddebug
gotopage /cgi-bin/packages_opkg.cgi



