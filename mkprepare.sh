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

if ! test -e dl/Alt-F-utils-0.1.tar.gz; then
	cp package/Alt-F-utils/Alt-F-utils-0.1.tar.gz dl
fi

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

echo "Building needed host tools and copying then to the bin dir. No checks done!"

# just to be sure
(cd  bin; rm devio  dns323-fw  lzma  mkimage  mksquashfs)

cd host-tools

# just to be sure
rm -rf Alt-F-utils-0.1 squashfs4.0-lzma-snapshot devio-1.2 uboot-mkimage lzma465

tar xzf devio-1.2.tar.gz
cd devio-1.2
./configure
make
cp src/devio ../../bin/
cd ..

tar xzf debian-uboot-mkimage_0.4.tar.gz
cd uboot-mkimage
make
cp mkimage ../../bin/
cd ..

mkdir lzma465 # must be a windows gui
tar -C lzma465 -xjf lzma465.tar.bz2
cd lzma465
cd CPP/7zip/Compress/LZMA_Alone
make -f makefile.gcc
cp lzma ../../../../../../bin
cd ../../../../..

tar xzf squashfs4.0-lzma-snapshot.tgz
cd squashfs4.0-lzma-snapshot/squashfs-tools/
sed -i 's/#LZMA_SUPPORT = 1/LZMA_SUPPORT = 1/' Makefile
sed -i 's|../../LZMA/lzma465|../../lzma465|' Makefile 
make
cp mksquashfs ../../../bin/
cd ../../

tar xzf ../package/Alt-F-utils/Alt-F-utils-0.1.tar.gz \
	Alt-F-utils-0.1/dns323-fw.c
cd Alt-F-utils-0.1/
make dns323-fw
cp dns323-fw ../../bin/
cd ../..

