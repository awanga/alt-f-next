#!/bin/sh

cleanup() {
	echo "</pre><h4>An error has occurred, cleaning up.</h4>$(back_button)</body></html>"
	clean
	exit 0
}

clean() {
	rm -f data.tar.gz cdebootstrap-static_0.5.4_armel.deb

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

if test "$submit" = "Install"; then

	if test -z "$mirror" -o "$mirror" = "none"; then
		msg "You have to specify a mirror near you in order to download Debian"
	fi

	DEBMIRROR=$(httpd -d $mirror)

	if test -f $DEBDIR/boot/vmlinuz-*-orion5x -a -f $DEBDIR/boot/initrd.img-*-orion5x; then
		msg "Debian is already installed in this filesystem."
	fi

	write_header "Installing Debian"

	echo "<small><h4>Downloading installer...</h4><pre>"

	cd /tmp
	wget --progress=dot:binary $DEBMIRROR/pool/main/c/cdebootstrap/cdebootstrap-static_0.5.4_armel.deb
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Extracting installer...</h4><pre>"

	ar x cdebootstrap-static_0.5.4_armel.deb data.tar.gz
	if test $? != 0; then cleanup; fi

	filelist=$(tar -tzf data.tar.gz)
	tar -C / -xzf data.tar.gz
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Downloading and installing Debian, this might take some time...</h4><pre>"

	mkdir -p $DEBDIR 
	cdebootstrap-static --allow-unauthenticated --arch=armel \
		--include=linux-image-2.6.32-5-orion5x,openssh-server,kexec-tools \
		squeeze $DEBDIR $DEBMIRROR
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Debian installed successfully.</h4>"

	echo "<h4>Updating packages....</h4><pre>"

	chroot $DEBDIR /usr/bin/apt-get update

	echo "</pre><h4>Downloading and installing Alt-F in Debian...</h4><pre>"

	ver=$(cat /etc/Alt-F)
	wget --progress=dot:mega http://alt-f.googlecode.com/files/Alt-F-${ver}.tar 
	if test $? != 0; then cleanup; fi
	tar -xf Alt-F-${ver}.tar
	if test $? != 0; then cleanup; fi
	mv alt-f/rootfs.arm.cpio-sq.lzma $DEBDIR/boot/Alt-F-rootfs.arm.cpio-sq.lzma
	mv alt-f/zImage $DEBDIR/boot/Alt-F-zImage
	rm -rf alt-f Alt-F-${ver}.tar 

	cat<<-EOF > $DEBDIR/usr/sbin/alt-f
		#!/bin/bash

		if test "\$(runlevel | cut -d" " -f1)" != "1"; then
			echo -e "Debian is not being cleanly shutdown.\n"\
				"You should go to runlevel 1 by issuing the \"init 1\" command\n"\
				"before executing this command, or help me fix this script."
			exit 1
		fi

		kexec -l /boot/Alt-F-zImage --initrd=/boot/Alt-F-rootfs.arm.cpio-sq.lzma \
			--command-line="console=ttyS0,115200" && kexec -e
	EOF
	chmod +x $DEBDIR/usr/sbin/alt-f

	echo "</pre><h4>Setting up some Debian installation details...</h4><pre>"
	
	echo "<p>Enabling serial port acess..."

	sed -i 's/^[1-6]:/#&/' $DEBDIR/etc/inittab
	echo "T0:1235:respawn:/sbin/getty -n -l /bin/bash -L ttyS0 115200 vt100" >> $DEBDIR/etc/inittab

	echo "<p>Setting /etc/fstab..."

	cat<<-EOF > $DEBDIR/etc/fstab
		proc	/proc	proc	defaults	0	0
		sysfs	/sys	sysfs	defaults	0	0
		/dev/$DEBDEV	/	$(blkid -sTYPE -o value /dev/$DEBDEV)	defaults	1	1
	EOF

	for i in $(blkid -t TYPE=swap -o device); do
		echo "$i	swap	swap	defaults	0	0" >> $DEBDIR/etc/fstab
	done

	echo "<p>Using same ssh host key as Alt-F is using now..."

	for i in ssh_host_dsa_key ssh_host_rsa_key ssh_host_dsa_key.pub ssh_host_rsa_key.pub; do
		mv $DEBDIR/etc/ssh/$i $DEBDIR/etc/ssh/${i}-orig
	done

	dropbearconvert dropbear openssh /etc/dropbear/dropbear_rsa_host_key $DEBDIR/etc/ssh/ssh_host_rsa_key 
	dropbearconvert dropbear openssh /etc/dropbear/dropbear_dss_host_key $DEBDIR/etc/ssh/ssh_host_dsa_key 

	echo "<p>Setting root default password..."

	chroot $DEBDIR /bin/bash -c "/bin/echo root:$(cat /etc/web-secret) | /usr/sbin/chpasswd"
	if test $? != 0; then cleanup; fi

	clean

	echo "</pre><h4>Success.</h4>"
	cat<<-EOF
		<script type="text/javascript">
			setTimeout(function() {window.location.assign(document.referrer);}, 3000)
		</script>
	EOF
	exit 0

elif test "$submit" = "Uninstall"; then

	html_header
	busy_cursor_start

	for i in bin boot dev etc home initrd.img lib media mnt opt proc root sbin selinux \
			srv sys tmp usr var vmlinuz; do
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

	html_header 
	echo "<h3><center>Executing Debian...</center></h3><pre>"

	debian kexec
	
	echo "</pre><h4>failed.</h4> $(back_button)</body></html>"
fi

#enddebug


