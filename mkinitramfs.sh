#!/bin/bash

#set -x

# recursively find packages that <package> depends on: 
rdeps() {
	if ! grep -q ^BR2_PACKAGE_$(echo $1 | tr '[:lower:]-' '[:upper:]_')=y $CWD/.config; then return; fi
	echo $1 $(awk '/Version:/{print $2}' $CWD/ipkgfiles/$1.control)
	deps=$(awk '/Depends:/{for (i=2; i<=NF; i++) print $i}' $CWD/ipkgfiles/$1.control)
	for i in $deps; do
		p=${i%%,}
		if ! test "$p" = "ipkg"; then rdeps $p; fi
	done
}

# preinst.status needed at runtime to avoid installing pre installed packages
# when they are dependencies of a new package being installed
deps_status() {
	grep -E '(Package:|Version:|Depends:|Architecture:)' $CWD/ipkgfiles/$1.control
	echo "Status: install user installed"
	echo "Installed-Time: $(date +%s)"
					
	if test -f $CWD/ipkgfiles/$1.conffiles; then
		echo Conffiles: 
		for j in $(cat $CWD/ipkgfiles/$1.conffiles); do
			echo "$j $(md5sum $BLDDIR/project_build_arm/$board/root/$j | cut -d" " -f1)"
		done
	fi  
	echo
}

deps_check() {
	if ! ( cd $CWD; ./mkpkg.sh -check $1 >& /dev/null); then
		echo "WARNING: Package $1 does not contains all files, might or not be OK!" > $(tty)
	fi
}

beroot() {
	if test $(whoami) != "root"; then
		sudo -E $0 $TYPE $COMP
		exit $?
	fi
}

usage() {
	echo "Usage: mkinitramfs [type] (cpio|squsr|sqall*|sqsplit) [compression] (gz|lzma|xz*)"
	exit 1
}

if test "$(dirname $0)" != "."; then
	echo "mkinitramfs: This script must be run in the root of the tree, exiting."
	exit 1;
fi

if test -z "$BLDDIR"; then
	echo "mkinitramfs: Run '. exports [board]' first."
	exit 1
fi

if test "$#" = 0; then
	TYPE=sqall
	COMP=xz
elif test "$#" = 1; then
	if test "$1" = "cpio" -o "$1" = "squsr" -o "$1" = "sqall" -o "$1" = "sqsplit"; then
		TYPE=$1
		COMP=xz
	elif test "$1" = "gz" -o "$1" = "lzma" -o "$1" = "xz"; then
		TYPE=sqall
		COMP=$1
	else
		usage
	fi
elif test "$#" = 2; then
	TYPE=$1
	COMP=$2
else
	usage
fi

if test $TYPE != "cpio" -a $TYPE != "squsr" -a $TYPE != "sqall" -a "$1" != "sqsplit" \
	-a $COMP != "gz" -a $COMP != "lzma" -a $COMP != "xz"; then
	usage
fi

if test -z "$ME" -o -z "$MG"; then
	export ME=$(id -un)
	export MG=$(id -gn)
fi

. .config 2> /dev/null
board=$BR2_PROJECT
kver=$BR2_CUSTOM_LINUX26_VERSION

EXT=$COMP
if test "$COMP" = "xz"; then
	cmd="xz --check=crc32 -z -6"
elif test "$COMP" = "lzma"; then
	cmd="lzma -6"
elif test "$COMP" = "gz"; then
	cmd="gzip -9"
	COMP=gzip
else
	echo "mkinitramfs: unknown compressor."
	exit 1
fi

# FIXME: shouldn't this be in .config instead? to diminish redundancy and missing dependencies?
# fw_pkgs: pre-installed packages in base firmware
# sq_pkgs: pre-installed packages on sqimage 
# base_pkgs/base_pkgs2 contains all packages for the base firmware but uClibc and busybox.
# Other packages often don't explicitly depends on them, so we have to list them all here.
base_pkgs="alt-f-utils mdadm e2fsprogs dosfstools ntfs-3g gptfdisk-sgdisk sfdisk dropbear portmap nfs-utils kexec openssl zlib popt"
base_pkgs2="inadyn-mt smartmontools at ntp-common cifs-utils openssh-sftp vsftpd rsync wget msmtp stunnel libiconv"

# SQFSBLK: squashfs compression block sizes: 131072 262144 524288 1048576
SQFSBLK=131072

case $board in
	dns323|qemu)
		SQFSBLK=262144
		fw_pkgs="$base_pkgs $base_pkgs2 samba-small"
		all_pkgs=$fw_pkgs
		;;
	dns325|dns327)
		if test $# = 0; then
			TYPE="sqsplit"
			COMP=xz
		fi
		fw_pkgs="$base_pkgs mtd-utils"
		sq_pkgs="$base_pkgs2  samba gptfdisk ntfs-3g-ntfsprogs btrfs-progs dnsmasq quota-tools minidlna netatalk forked-daapd transmission sqlite"
		all_pkgs="$fw_pkgs $sq_pkgs"
		;;
	*) echo "mkinitramfs: Unsupported \"$board\" board"; exit 1;;
esac

CWD=$PWD

# base packages /etc configuration files
base_conf=$(for i in $base_pkgs $base_pkgs2; do grep './etc/' $CWD/ipkgfiles/$i.lst; done)

# all packages (and needed dependencies) /etc configuration files
all=$(for i in $all_pkgs; do rdeps $i; done | sort -u | cut -d" " -f1)
all_conf=$(for i in $all; do grep './etc/' $CWD/ipkgfiles/$i.lst; done)

# deprecated
if test "$TYPE" = "cpio"; then # standard initramfs
	beroot

	cd ${BLDDIR}/binaries/$board
	mkdir -p tmp

	mount -o ro,loop rootfs.arm.ext2 tmp
	cd tmp
	find . | cpio --quiet -o -H newc | $cmd > ../rootfs.arm.$TYPE.$EXT
	cd ..
	umount tmp
	rmdir tmp

	chown $ME:$MG rootfs.arm.$TYPE.$EXT

# deprecated
elif test "$TYPE" = "squsr"; then # standard initramfs with /usr squashed
	beroot

	cd ${BLDDIR}/binaries/$board
	mkdir -p tmp

	cp rootfs.arm.ext2 rootfs.arm.ext2.tmp
	mount -o loop rootfs.arm.ext2.tmp tmp

	mksquashfs tmp/usr/ usr.squashfs -comp $COMP -b $SQFSBLK \
		-always-use-fragments -keep-as-directory -all-root
	rm -rf tmp/usr/*
	mv usr.squashfs tmp
	cd tmp

	find . | cpio --quiet -o -H newc | $cmd > ../rootfs.arm.$TYPE.$EXT
	cd ..
	umount tmp
	rmdir tmp
	rm rootfs.arm.ext2.tmp

	chown $ME:$MG rootfs.arm.$TYPE.$EXT

# DNS-321/323
elif test "$TYPE" = "sqall"; then # squashfs initrd, everything squashed

	cd ${BLDDIR}/project_build_arm/$board/

	fw_pkgs_deps=$(for i in $fw_pkgs; do rdeps $i; done | sort -u)

	# create ipkg status file stating which packages are pre installed
	echo "$fw_pkgs_deps" | sort -u > root/etc/preinst
	rm -f root/etc/preinst.status
	for i in $(echo "$fw_pkgs_deps" | cut -d' ' -f1); do
		deps_check $i
		deps_status $i
	done >> root/etc/preinst.status
	
	# update /etc/settings with pre installed package configuration files
	echo -e "$base_conf\n$all_conf" | sort | uniq -u | grep -vE '/etc/init.d|/etc/avahi/services' | sed 's|^./|/|' >> root/etc/settings

	# mksquashfs can create device nodes
	rm -f root/dev/null root/dev/console
	if ! test -f $CWD/mksquashfs.pf; then
		cat<<-EOF > $CWD/mksquashfs.pf
		/dev/null c 666 root root 1 3
		/dev/console c 600 root root 5 1
		EOF
	fi
	mksquashfs root rootfs.arm.$TYPE.$EXT -comp $COMP -noappend -b $SQFSBLK \
		-always-use-fragments -all-root -pf $CWD/mksquashfs.pf

	mv rootfs.arm.sqall.$EXT ${BLDDIR}/binaries/$board

# DNS-320/325/327
elif test "$TYPE" = "sqsplit"; then # as 'sqall' above but also create sqimage with extra files

	if test "$board" != "dns325" -a "$board" != "dns327"; then
		echo "mkinitramfs: ERROR, \"sqsplit\" is only for a dns-320/325/327"
		exit 1
	fi

	cd ${BLDDIR}/project_build_arm/$board/

	fw_pkgs_deps=$(for i in $fw_pkgs; do rdeps $i; done | sort -u)
	sq_pkgs_deps=$(for i in $sq_pkgs; do rdeps $i; done | sort -u)

# HACK! with the dns327 we now have two architectures, armv5 and armv7.
# armv5 binaries are the default and runs on both archs, but kernel modules are different for both.
# The ideal situation would be to have the kernel-modules pkg to depends on the armv5 OR the armv7 
# kernel-modules pkg, and at install time 'ipkg' would read the running machine arch and install
# the appropriate kernel-module pkg. But that does not seems to be possible.
# instead, the no-files kernel-modules pkg install script does that.
# So the kernel-modules pkg has no actual kernel modules files, and one has to determine the pkgs
# file list at build time here:

	if echo $sq_pkgs_deps | grep -q kernel-modules; then
		if test $board = "dns327"; then
			sq_pkgs_deps=$(echo -e "$sq_pkgs_deps\nkernel-modules-armv7 $kver")
		else
			sq_pkgs_deps=$(echo -e "$sq_pkgs_deps\nkernel-modules-armv5 $kver")
		fi
	fi

	# bug 363: remove from sq_pkgs_deps any entries already in fw_pkgs_deps
	sq_pkgs_deps=$(echo -e "$fw_pkgs_deps\n$fw_pkgs_deps\n$sq_pkgs_deps" | sort | uniq -u)
	#echo -e "$fw_pkgs_deps" | sort -u > $CWD/fw
	#echo -e "$sq_pkgs_deps" | sort -u > $CWD/sq

	echo -e "$fw_pkgs_deps\n$sq_pkgs_deps" | sort -u > root/etc/preinst

	# create ipkg status file stating which packages are pre installed
	rm -f root/etc/preinst.status
	for i in $(echo "$fw_pkgs_deps" | cut -d' ' -f1); do
		deps_check $i
		deps_status $i
	done >> root/etc/preinst.status

	# update /etc/settings with pre installed package configuration files
	echo -e "$base_conf\n$all_conf" | sort | uniq -u | grep -vE '/etc/init.d|/etc/avahi/services' | sed 's|^./|/|' >> root/etc/settings
	
	# create sqimage pkgs file list and ipkg status file stating which packages are pre installed
	TF=$(mktemp)
	for i in $(echo "$sq_pkgs_deps" | cut -d' ' -f1); do
		deps_check $i
		deps_status $i
		cat $CWD/ipkgfiles/$i.lst >> $TF
	done >> root/etc/preinst.status 

	# sqimage files list, to be removed from base and present only on sqimage
	sqimagefiles=$(cat $TF | sort -u)
	rm $TF

	rm -rf image sqimage
	cp -a root image
	mkdir -p sqimage
	cd image
	# create dirs first, as packages often don't have dirs name on it
	# and its permission needs to be preserved
	find . -type d | cpio -p ../sqimage 
	echo "$sqimagefiles" | cpio -pu ../sqimage
	rm -f $sqimagefiles >& /dev/null
	cd ..
	# remove empty dirs on sqimage (image itself *has* to have them)
	find sqimage -depth -type d -empty -exec rmdir {} \;
	
	rm -f image/dev/null image/dev/console # mksquashfs can create device nodes
	if ! test -f $CWD/mksquashfs.pf; then
		cat<<-EOF > $CWD/mksquashfs.pf
		/dev/null c 666 root root 1 3
		/dev/console c 600 root root 5 1
		EOF
	fi
	mksquashfs image rootfs.arm.sqall.$EXT -comp $COMP -noappend -b $SQFSBLK \
		-always-use-fragments -all-root -pf $CWD/mksquashfs.pf

	mksquashfs sqimage rootfs.arm.sqimage.$EXT -comp $COMP -noappend -b $SQFSBLK \
		-always-use-fragments -all-root

	mv rootfs.arm.sqall.$EXT rootfs.arm.sqimage.$EXT ${BLDDIR}/binaries/$board

else
	usage
fi



