#!/bin/bash

if test "$(dirname $0)" != "."; then
	echo "This script must be run in the root of the tree, exiting."
	exit 1;
fi

if test -z "$BLDDIR"; then
	cat<<-EOF
		Set the environment variable BLDDIR to the build directory, e.g
		   export BLDDIR=<path to where you which the build dir>\nkeep it out of this tree."
		exiting.
	EOF
	exit 1
fi

DESTD=$BLDDIR/binaries/dns323

case $1 in
	sqfs) rootfs="rootfs.arm.cpio-sq.lzma" ;;
	gz) rootfs="rootfs.arm.cpio.gz" ;;
	lzma) rootfs="rootfs.arm.cpio.lzma" ;;
	*)	echo "Usage: mkreloaded gz | lzma | sqfs"
		exit
		;;
esac

# *must* use make-3.81, build and installed by mkprepare.sh
PATH=$(pwd)/bin:$PATH

if ! test -f ${DESTD}/zImage -a -f ${DESTD}/$rootfs; then
	echo "${DESTD}/zImage or ${DESTD}/$rootfs not found, exiting"
	exit 1
fi

if test ${DESTD}/rootfs.arm.ext2 -nt ${DESTD}/$rootfs; then
	echo "${DESTD}/rootfs.arm.ext2 is newer than ${DESTD}/$rootfs,  exiting"
	exit 1
fi

ver=$(cut -f2 -d" " customroot/etc/Alt-F)

cd reloaded

if ! test -f alt-f/README.INSTALL -a -f alt-f/README.USE; then
	mkdir -p alt-f
	if test -d ../../wiki; then
		(cd ../../wiki; svn update)
		cp ../../wiki/HowToInstall.wiki ../README.INSTALL
	fi
	if ! cp ../README.INSTALL alt-f/README.INSTALL; then exit 1; fi
	cp ../LICENCE ../COPYING alt-f
fi

# the plain fonz reloaded:
if false; then
	if ! test -f alt-f/reloaded-2.6.12.6-arm1.ko; then
		if ! test -f ffp-reloaded-0.5-2.tgz; then
			wget http://www.inreto.de/dns323/ffp-reloaded/packages/ffp-reloaded-0.5-2.tgz
		fi
		tar --wildcards -xzf ffp-reloaded-0.5-2.tgz ./ffp/boot/reloaded-\*
		mv ffp/boot/reloaded-* alt-f
		rm -rf ffp
	fi
else # don't use panic() on fail, load initrd at 0x600000, putterboy

	# Orion based SoCs
	# DNS-321: 2.6.22.7
	# DNS-323: 2.6.12.6
	# DNS-343: 2.6.22.7

	# Kirkwood based SoCs
	# DNS-320: 2.6.22.18, reloaded does not seems to work

	kvers="2.6.12.6 2.6.15"

	karch_2_6_12_6="2.6.12.6-arm1"
	vermagic_2_6_12_6="#define VERMAGIC_STRING \"$karch_2_6_12_6 ARMv5 gcc-3.3\""

	if ! test $(which arm-linux-uclibcgnueabi-gcc); then
		echo "arm-linux-uclibcgnueabi-gcc is not in PATH"
		exit 1
	fi

	for i in $kvers; do
		if ! test -f ../dl/linux-${i}.tar.bz2; then
			echo "Downloading linux-$i"
			wget -P ../dl http://www.kernel.org/pub/linux/kernel/v2.6/linux-${i}.tar.bz2
		fi
	done

	for i in $kvers; do
		if ! test -d linux-$i; then
			echo "Extracting linux-$i"
			tar xjf ../dl/linux-${i}.tar.bz2
			cd linux-$i
			echo "Configuring linux-$i"
			# gross hack...
			kver_=$(echo $i | tr '.' '_')
			kmagic=$(eval echo \$vermagic_$kver_)
			if test -n "$kmagic"; then
				echo "$kmagic" >> include/linux/vermagic.h
			fi
			make CROSS_COMPILE=arm-linux-uclibcgnueabi- ARCH=arm defconfig modules_prepare
			if test $? != 0; then exit 1; fi
			cd ..
		fi
	done

	if ! test -f dns323-reloaded-0.7.167.tar.gz; then
		wget http://www.inreto.de/dns323/reloaded/dns323-reloaded-0.7.167/dns323-reloaded-0.7.167.tar.gz
	fi

	if ! test -d dns323-reloaded-0.7.167; then
		tar -xzf dns323-reloaded-0.7.167.tar.gz
		patch -p0 < dns323-reloaded-0.7.167.patch
	fi

	cd dns323-reloaded-0.7.167
	for i in $kvers; do
		kver_=$(echo $i | tr '.' '_')
		karch=$(eval echo \$karch_$kver_)
		if test -z "$karch"; then
			karch=$i
		fi
		if ! test -f reloaded-${i}.ko; then
			echo "Building reloaded for linux-$i"
			rm linux
			ln -sf ../linux-$i linux
			make clean
			FUN_TARGET=arm-linux-uclibcgnueabi make
			mv reloaded.ko reloaded-${karch}.ko
			cp reloaded-${karch}.ko ../alt-f/
		fi
	done
	cd ..
fi

if test -e $DESTD/zImage -a -e $DESTD/$rootfs; then
	rm -f alt-f/rootfs.arm.cpio*
	cp $DESTD/zImage $DESTD/$rootfs alt-f
else
	echo "${DESTD}/zImage or ${DESTD}/$rootfs not found, exiting"
	exit 1
fi

# don't compress, no significant space saving and much slower extraction
rm alt-f/*~ >& /dev/null
tar --exclude-vcs -cvf Alt-F-$ver.tar alt-f
mv Alt-F-$ver.tar $DESTD
cp fun_plug $DESTD
