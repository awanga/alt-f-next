#!/bin/sh

cd host-tools

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

