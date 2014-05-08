#!/bin/sh

cleanup() {
	echo "</pre><h4>An error has occurred, cleaning up.</h4>$(back_button)</body></html>"
	clean
	exit 0
}

clean() {
	rm -f data.tar.gz $CDEBOOT

	for i in $filelist; do
		if test -f /$i; then
			rm -f /$i >& /dev/null
		fi
	done

	for i in $(echo $filelist | tr ' ' '\n' | sort -r); do
		if test -d /$i; then
			rmdir /$i  >& /dev/null
		fi
	done
}

. common.sh
check_cookie
read_args

#debug

if test -z "$part" -o "$part" = "none"; then
	msg "You have to specify the filesystem where to install Debian"
fi

DEBDEV=$part
DEBDIR=/mnt/$DEBDEV 

if ! test -d "$DEBDIR"; then
	DEBDIR="$(awk '/'$part'/{print $2}' /proc/mounts)"
fi

if test "$submit" = "Install"; then

	if test -z "$mirror" -o "$mirror" = "none"; then
		msg "You have to specify a mirror near you in order to download Debian"
	fi

	if grep -qE 'DNS-320-A1A2|DNS-325-A1A2' /tmp/board ; then SoC=kirkwood; else SoC=orion5x; fi

	DEBMIRROR=$(httpd -d $mirror)

	if test -f $DEBDIR/boot/vmlinuz-*-$SoC -a -f $DEBDIR/boot/initrd.img-*-$SoC; then
		msg "Debian is already installed in this filesystem."
	fi

	CDEBOOT=$(wget -q -O - $DEBMIRROR/pool/main/c/cdebootstrap/ | sed -n 's/.*>\(cdebootstrap-static_.*_armel.deb\)<.*/\1/p' | tail -1)

	write_header "Installing Debian"

	echo "<small><h4>Downloading installer...</h4><pre>"

	cd /tmp
	wget --progress=dot:binary $DEBMIRROR/pool/main/c/cdebootstrap/$CDEBOOT
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Extracting installer...</h4><pre>"

	ar x $CDEBOOT data.tar.gz
	if test $? != 0; then cleanup; fi

	filelist=$(tar -tzf data.tar.gz)
	tar -C / -xzf data.tar.gz
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Downloading and installing Debian, this might take some time...</h4><pre>"

	mkdir -p $DEBDIR 
	cdebootstrap-static --allow-unauthenticated --arch=armel \
		--include=linux-image-$SoC,openssh-server,kexec-tools,mdadm \
		wheezy $DEBDIR $DEBMIRROR
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Debian installed successfully.</h4>"

	echo "<h4>Updating packages....</h4><pre>"

	chroot $DEBDIR /usr/bin/apt-get update

	mdadm --detail --test /dev/$DEBDEV >& /dev/null
	if test $? -lt 2; then # allow degraded but working RAID

		echo "</pre><h4>Adding RAID boot support....</h4><pre>"

		mount -o bind  /proc $DEBDIR/proc
		mount -o bind  /sys  $DEBDIR/sys
		mount -o bind  /dev  $DEBDIR/dev

		chroot $DEBDIR /usr/sbin/update-initramfs -u

		umount $DEBDIR/proc
		umount $DEBDIR/sys
		umount $DEBDIR/dev
	fi

	vers="$(cat /etc/Alt-F) 0.1RC3 0.1RC2" # fallback
	echo "</pre><h4>Downloading and installing Alt-F into Debian...</h4><pre>"
	for ver in $vers; do
		sites="http://sourceforge.net/projects/alt-f/files/Releases/$ver http://alt-f.googlecode.com/files"
		for site in $sites; do
			echo "</pre><h5>Try downloading Alt-F-$ver from $site...</h5><pre>"
			wget --progress=dot:mega $site/Alt-F-${ver}.tar 
			if test $? = 0; then
				altf_down="ok"
				break		
			fi
		done
		if test -n "$altf_down"; then
			break
		fi
	done
	if test -z "$altf_down"; then
		echo "</pre><h4>Downloading Alt-F $ver failed...</h4><pre>"
		cleanup
	fi

	tar -xf Alt-F-${ver}.tar
	if test $? != 0; then cleanup; fi
	rootfs=$(basename $(ls alt-f/rootfs.arm.*))
	mv alt-f/$rootfs $DEBDIR/boot/Alt-F-$rootfs
	mv alt-f/zImage $DEBDIR/boot/Alt-F-zImage
	rm -rf alt-f Alt-F-${ver}.tar 

	echo "</pre><h4>Setting up some Debian installation details...</h4>"
	
	echo "<p>Enabling serial port acess..."

	sed -i 's/^[1-6]:/#&/' $DEBDIR/etc/inittab
	echo "T0:1235:respawn:/sbin/getty -n -l /bin/bash -L ttyS0 115200 vt100" >> $DEBDIR/etc/inittab

	echo "<p>Changing Debian message of the day..."

	echo -e "\nYou leaved Alt-F, you are now on your own.\nTo return to Alt-F, execute the command 'alt-f',\n" >> $DEBDIR/etc/motd.tail

	echo "<p>Using same ssh host key as Alt-F is using now...<pre>"

	for i in ssh_host_dsa_key ssh_host_rsa_key ssh_host_dsa_key.pub ssh_host_rsa_key.pub; do
		mv $DEBDIR/etc/ssh/$i $DEBDIR/etc/ssh/${i}-orig
	done

	dropbearconvert dropbear openssh /etc/dropbear/dropbear_rsa_host_key $DEBDIR/etc/ssh/ssh_host_rsa_key 
	dropbearconvert dropbear openssh /etc/dropbear/dropbear_dss_host_key $DEBDIR/etc/ssh/ssh_host_dsa_key
	chmod og-rw $DEBDIR/etc/ssh/*
	chown root $DEBDIR/etc/ssh/*

	echo "</pre><p>Setting root password the same as Alt-F web admin password..."

	chroot $DEBDIR /bin/bash -c "/bin/echo root:$(cat /etc/web-secret) | /usr/sbin/chpasswd"
	if test $? != 0; then cleanup; fi

	cp $DEBDIR/etc/default/kexec $DEBDIR/etc/default/kexec-debian
	cp $DEBDIR/etc/default/kexec $DEBDIR/etc/default/kexec-alt-f
	sed -i -e 's|^KERNEL_IMAGE.*|KERNEL_IMAGE="/boot/Alt-F-zImage"|' \
		-e 's|^INITRD.*|INITRD="/boot/Alt-F-'$rootfs'"|' \
		$DEBDIR/etc/default/kexec-alt-f
	cat<<-EOF > $DEBDIR/usr/sbin/alt-f
		#!/bin/bash
		cp /etc/default/kexec-alt-f /etc/default/kexec
		reboot
	EOF
	chmod +x $DEBDIR/usr/sbin/alt-f

	clean

	echo "<h4>Success.</h4>$(goto_button Continue /cgi-bin/debian.cgi)</body></html>"

elif test "$submit" = "Uninstall"; then

	html_header "Uninstalling Debian..."
	busy_cursor_start

	for i in bin boot dev etc home initrd.img lib media mnt opt proc root sbin selinux \
			srv sys tmp usr var vmlinuz; do
		echo "Removing $DEBDIR/$i...<br>"
		rm -rf $DEBDIR/$i >& /dev/null
	done

	busy_cursor_end
	cat<<-EOF
		<script type="text/javascript">
			window.location.assign(document.referrer)
		</script></body></html>
	EOF

elif test "$submit" = "Execute"; then

	part=/dev/$(basename $DEBDIR)

	html_header "Executing Debian"

	debian -kexec > /dev/null
	
	echo "</body></html>"
fi

#enddebug
