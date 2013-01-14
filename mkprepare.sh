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

# kernel patches are now in toolchain/kernel-headers
# and are applied automatically
#if ! test -e dl/aufs+sqfs4lzma-2.6.33.patch; then
#	cp patches/aufs+sqfs4lzma-2.6.33.patch dl
#fi

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
	if ! ln -sf $(pwd)/dl "$BLDDIR/dl"; then
		echo "Unable to link, exiting."
		exit 1
	fi
fi

echo -e "\nBuilding needed host tools and copying then to the bin dir.\n\nNo checks done!\n\n"

# just to be sure
mkdir -p bin
(cd bin; rm -f *)

cd host-tools

# Alt-F-utils version
eval $(cat ../package/Alt-F-utils/Alt-F-utils.mk | grep ^ALT_F_UTILS_VERSION | tr -d ' ')
AFV=$ALT_F_UTILS_VERSION

# just to be sure
rm -rf Alt-F-utils-$AFV squashfs4.0-lzma-snapshot devio-1.2 uboot-mkimage 7z465 ipkg-utils-050831

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
sed -i '1s/python/python -W ignore/' ../bin/ipkg-make-index
sed -i 's/.*Packaged contents.*/#&/' ../bin/ipkg-build

# some old Makefiles (including some linux kernel sources) are not accepted
# by make version greater than 3.81, so install 3.81.
# you have to put the Alt-F bin directory in your path *before* the standard path, as in
# export PATH=<Alt-F bin directory>:$PATH
# NEWS: busybox has a patch to deal with the issue, kernel 2.6.15 is not used by default,
# so this might not be needed. Anyway copy it to the tools bin with a clear name
if ! test -e make-3.81.tar.bz2; then
	wget http://ftp.gnu.org/pub/gnu/make/make-3.81.tar.bz2
fi
rm -rf make-3.81
tar xjf make-3.81.tar.bz2
cd make-3.81
./configure
make
cp make ../../bin/make-3.81
cd ..

if ! test -e mklibs_0.1.31.tar.gz; then
	# wget http://ftp.de.debian.org/debian/pool/main/m/mklibs/mklibs_0.1.31.tar.gz
	# use snapshot.debian.org to get old packages
	wget http://snapshot.debian.org/archive/debian/20101225T025119Z/pool/main/m/mklibs/mklibs_0.1.31.tar.gz

fi
rm -rf mklibs_0.1.31
tar xzf mklibs_0.1.31.tar.gz
mv mklibs mklibs_0.1.31
# needed on 64-bit Archlinux, submited by neosisani under issue 127
sed -i '/#include <fcntl.h>/i#include <unistd.h>' mklibs_0.1.31/src/mklibs-readelf/elf.cpp
cd mklibs_0.1.31
./configure
make
cp src/mklibs-readelf/mklibs-readelf src/mklibs-copy src/mklibs ../../bin
# there are things installed in usr/lib/mklibs, see if they are needed.
# test with "make install DESTDIR=<some tmp dir>"
cd ..
 
