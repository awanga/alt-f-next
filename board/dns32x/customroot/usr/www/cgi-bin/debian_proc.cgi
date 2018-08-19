#!/bin/sh

cleanup() {
	echo "</pre><h4>An error has occurred, cleaning up.</h4>$(back_button)</body></html>"
	clean
	exit 0
}

clean() {
	rm -f data.tar.* control.tar.* debian-binary $CDEBOOT

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

	board=$(cat /tmp/board)
	mod=${board%-*}
	rev=${board##*-}
	if test "$mod" = 'DNS-323'; then
		rev=AxBxCx;
	fi

	case "$mod" in
		DNS-321|DNS-323)
			SoC=orion5x
			arch=armel
			linuximg=linux-image-$SoC
			;;
		DNS-320|DNS-320L|DNS-325)
			SoC=kirkwood
			arch=armel
			linuximg=linux-image-$SoC
			;;
		DNS-327L)
# Alt-F kernel has to have Thumb user support and VFP configured
# debian armhf requirements: ARMv7-A + Thumb-2 + VFPv3D16 
			SoC=armmp 
			arch=armhf
			linuximg=linux-image-$SoC # armel doesn't has a linux-image for armmp in jessie
			;;
		*)
			msg "Unknown Debian installer architecture for $board" ;;
	esac

	DEBMIRROR=$(httpd -d $mirror)

	if test -f $DEBDIR/boot/vmlinuz-*-$SoC -a -f $DEBDIR/boot/initrd.img-*-$SoC; then
		msg "Debian is already installed in this filesystem."
	fi

	# cdebootstrap-static contains a static binary and a standalone tar.
	# The standalone tar can be used on non-Debian systems. Use it instead under Alt-F?

	CDEBOOT=$(wget -q -O - $DEBMIRROR/pool/main/c/cdebootstrap/ | sed -n "s/.*>\(cdebootstrap-static_.*_$arch.deb\)<.*/\1/p" | tail -1)

	write_header "Installing Debian"

	echo "<small><h4>Downloading installer...</h4><pre>"

	cd /tmp
	wget --progress=dot:binary $DEBMIRROR/pool/main/c/cdebootstrap/$CDEBOOT
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Extracting installer...</h4><pre>"

	ar x $CDEBOOT
	if test $? != 0; then cleanup; fi

	if test -f data.tar.gz; then
		DCOMP="zcat data.tar.gz"
	elif test -f data.tar.xz; then
		if ! which xzcat >& /dev/null; then
			rm -f data.tar.* control.tar.* debian-binary $CDEBOOT
			msg "Debian Installer in \"xz\" format, you have to install the \"xz\" Alt-F package first."
		fi
		DCOMP="xzcat data.tar.xz"
	else
		msg "Unknown compressor"
	fi
	
	filelist=$($DCOMP | tar -tf -)
	$DCOMP | tar -C / -xf -
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Downloading and installing Debian, this might take some time...</h4><pre>"

	mkdir -p $DEBDIR 
	cdebootstrap-static --allow-unauthenticated --arch=$arch \
		--include=openssh-server,kexec-tools,mdadm,$linuximg \
		jessie $DEBDIR $DEBMIRROR
	if test $? != 0; then cleanup; fi

	echo "</pre><h4>Debian installed successfully.</h4>"

	echo "<h4>Updating packages....</h4><pre>"

	echo "deb $DEBMIRROR jessie-backports main" >> $DEBDIR/etc/apt/sources.list

	chroot $DEBDIR /usr/bin/apt-get update

#	mdadm --detail --test /dev/$DEBDEV >& /dev/null
#	if test $? -lt 2; then # allow degraded but working RAID

		echo "</pre><h4>Adding RAID boot support....</h4><pre>"

		mount -o bind  /proc $DEBDIR/proc
		mount -o bind  /sys  $DEBDIR/sys
		mount -o bind  /dev  $DEBDIR/dev

		chroot $DEBDIR /usr/sbin/update-initramfs -u

		umount $DEBDIR/proc
		umount $DEBDIR/sys
		umount $DEBDIR/dev
#	fi

	if test -n "$linuximg"; then # no linux-image, can't kexec into debian
		echo "</pre><h4>Fixing Debian links....</h4><pre>"
		for i in vmlinuz initrd.img; do
			if ! readlink -f $DEBDIR/$i > /dev/null; then
				pf=$(basename $(readlink $DEBDIR/$i))
				rm -f $DEBDIR/$i
				(cd $DEBDIR; ln -sf boot/$pf $i)
			fi
		done
		
		echo "</pre><h4>Downloading and installing Alt-F into Debian...</h4><pre>"
		
		ver=$(cat /etc/Alt-F)
		bfile=Alt-F-$ver-$mod-rev-$rev.bin
		site="http://sourceforge.net/projects/alt-f/files/Releases"
		
		echo "</pre><p>Downloading $bfile from $site/$ver...</p><pre>"

		if wget --progress=dot:mega $site/$ver/$bfile; then
			echo "</pre><p>Extracting Alt-F kernel and rootfs into Debian /boot...</p><pre>"
			if dns323-fw -s $bfile; then
				dd if=kernel of=$DEBDIR/boot/Alt-F-zImage bs=64 skip=1 >& /dev/null
				dd if=initramfs of=$DEBDIR/boot/Alt-F-rootfs.arm.sqmtd bs=64 skip=1 >& /dev/null

				cp $DEBDIR/etc/default/kexec $DEBDIR/etc/default/kexec-debian
				cp $DEBDIR/etc/default/kexec $DEBDIR/etc/default/kexec-alt-f
				sed -i -e 's|^KERNEL_IMAGE.*|KERNEL_IMAGE="/boot/Alt-F-zImage"|' \
					-e 's|^INITRD.*|INITRD="/boot/Alt-F-rootfs.arm.sqmtd"|' \
					-e 's|^APPEND.*|APPEND=" "|' \
					$DEBDIR/etc/default/kexec-alt-f
				cat<<-EOF > $DEBDIR/usr/sbin/alt-f
					#!/bin/bash
					cp /etc/default/kexec-alt-f /etc/default/kexec
					reboot
				EOF
				chmod +x $DEBDIR/usr/sbin/alt-f
				altf=1
			fi
		fi

		if test -z "$altf"; then
			echo "</pre><p>Downloading $bfile or extraction failed, can't restart Alt-F from within Debian.</p><pre>"
			cat<<-EOF > $DEBDIR/usr/sbin/alt-f
				#!/bin/bash
				reboot
			EOF
			chmod +x $DEBDIR/usr/sbin/alt-f
		fi
		rm -f $bfile kernel initramfs defaults
	fi
	
	echo "</pre><h4>Setting up some Debian installation details...</h4>"

	mkdir -p $DEBDIR/proc $DEBDIR/sys $DEBDIR/dev $DEBDIR/dev/pts $DEBDIR/tmp

	echo "<p>Changing Debian message of the day..."

	echo -e "\nYou leaved Alt-F, you are now on your own.\nTo return to Alt-F, execute the command 'alt-f',\n" >> $DEBDIR/etc/motd.tail
	cat $DEBDIR/etc/motd.tail >> $DEBDIR/etc/motd

	echo "<p>Using same ssh host key as Alt-F is using now...<pre>"

	for i in ssh_host_dsa_key ssh_host_rsa_key ssh_host_ecdsa_key \
		ssh_host_dsa_key.pub ssh_host_rsa_key.pub ssh_host_ecdsa_key.pub; do
		mv $DEBDIR/etc/ssh/$i $DEBDIR/etc/ssh/${i}-orig
	done

	dropbearconvert dropbear openssh /etc/dropbear/dropbear_rsa_host_key \
		$DEBDIR/etc/ssh/ssh_host_rsa_key 
	dropbearconvert dropbear openssh /etc/dropbear/dropbear_dss_host_key \
		$DEBDIR/etc/ssh/ssh_host_dsa_key
	dropbearconvert dropbear openssh /etc/dropbear/dropbear_ecdsa_host_key \
		$DEBDIR/etc/ssh/ssh_host_ecdsa_key
	chmod og-rw $DEBDIR/etc/ssh/*
	chown root $DEBDIR/etc/ssh/*

	echo "</pre><p>Setting the root password to be the same as Alt-F web admin password..."

	chroot $DEBDIR /bin/bash -c "/bin/echo root:$(cat /etc/web-secret) | /usr/sbin/chpasswd"
	if test $? != 0; then cleanup; fi

	echo "<p>Allowing ssh root password logins..."
	sed -i 's/PermitRootLogin.*/PermitRootLogin yes/' $DEBDIR/etc/ssh/sshd_config

	clean

	echo "<h4>Success.</h4>$(goto_button Continue /cgi-bin/debian.cgi)</body></html>"

elif test "$submit" = "Uninstall"; then

	html_header "Uninstalling Debian..."
	busy_cursor_start

	for i in run bin boot dev etc home initrd.img lib media mnt opt proc root sbin selinux \
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
