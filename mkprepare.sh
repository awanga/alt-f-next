#!/bin/sh

# do some housekeeping before the make.
# Only needs to be done once for each build tree.

if test "$(dirname $0)" != "."; then
	echo "This script must be run in the root of the tree, exiting."
	exit 1;
fi

if ! test -d dl; then
	echo "Creating download dir 'dl'"
	mkdir dl
fi

# This is now done during the make. commit 121
#if ! test -e dl/Alt-F-utils-0.1.tar.gz; then
#	cp package/Alt-F-utils/Alt-F-utils-0.1.tar.gz dl
#fi

if ! test -e dl/aufs+sqfs4lzma-2.6.33.patch; then
	cp patches/aufs+sqfs4lzma-2.6.33.patch dl
fi

if test -z "$BLDDIR"; then
	cat<<-EOF
		Set the environment variable BLDDIR to the build directory, e.g
		   export BLDDIR=<path to where you which the build dir>
		Keep it out of this tree.
		Exiting.
	EOF
	exit 1
fi

if ! test -d "$BLDDIR"; then
	echo "Creating $BLDDIR"
	if ! mkdir -p "$BLDDIR"; then
		echo "Unable to create it, exiting."
		exit 1
	fi
fi

if ! test -d "$BLDDIR/dl"; then
	echo "Linking $BLDDIR/dl to dl, to only download sources once"
	if ! ln -s $(pwd)/dl "$BLDDIR/dl"; then
		echo "Unable to link, exiting."
		exit 1
	fi
fi

echo -e "\nBuilding needed host tools and copying then to the bin dir.\n\nNo checks done!\n\n"

# just to be sure
(cd bin; rm *)

cd host-tools

# just to be sure
rm -rf Alt-F-utils-0.1 squashfs4.0-lzma-snapshot devio-1.2 uboot-mkimage 7z465 ipkg-utils-050831

if ! test -e devio-1.2.tar.gz; then
	wget http://sourceforge.net/projects/devio/files/devio/devio-1.2/devio-1.2.tar.gz/download
fi
tar xzf devio-1.2.tar.gz
cd devio-1.2
./configure
make
cp src/devio ../../bin/
cd ..

if ! test -e uboot-mkimage_0.4.tar.gz; then
	wget http://ftp.de.debian.org/debian/pool/main/u/uboot-mkimage/uboot-mkimage_0.4.tar.gz
fi
tar xzf uboot-mkimage_0.4.tar.gz
cd uboot-mkimage
make
cp mkimage ../../bin/
cd ..

if ! test -e 7z465.tar.bz2; then
	wget http://sourceforge.net/projects/sevenzip/files/7-Zip/4.65/7z465.tar.bz2/download
fi
mkdir 7z465 # must be a windows gui!
tar -C 7z465 -xjf 7z465.tar.bz2
cd 7z465
cd CPP/7zip/Compress/LZMA_Alone
make -f makefile.gcc
cp lzma ../../../../../../bin
cd ../../../../..

if ! test -e squashfs4.0-lzma-snapshot.tgz; then
	wget http://www.kernel.org/pub/linux/kernel/people/pkl/squashfs4.0-lzma-snapshot.tgz
fi
tar xzf squashfs4.0-lzma-snapshot.tgz
cd squashfs4.0-lzma-snapshot/squashfs-tools/
sed -i 's/#LZMA_SUPPORT = 1/LZMA_SUPPORT = 1/' Makefile
sed -i 's|../../LZMA/lzma465|../../7z465|' Makefile 
make
cp mksquashfs ../../../bin/
cd ../../

AFV=0.1.1 # Alt-F-utils version
if ! test -e Alt-F-utils-$AFV/dns323-fw.c; then
	mkdir Alt-F-utils-$AFV
	cp ../package/Alt-F-utils/Alt-F-utils-$AFV/dns323-fw.c \
		Alt-F-utils-$AFV
fi
cd Alt-F-utils-$AFV/
make dns323-fw
cp dns323-fw ../../bin/
cd ..

if ! test -e ipkg-utils-050831.tar.gz; then
	wget http://www.handhelds.org/download/packages/ipkg-utils/ipkg-utils-050831.tar.gz
fi
tar xzf ipkg-utils-050831.tar.gz
cp ipkg-utils-050831/ipkg-build \
	ipkg-utils-050831/ipkg-make-index \
	ipkg-utils-050831/ipkg.py \
	../bin
sed -i 's|*control|./control|' ../bin/ipkg.py
