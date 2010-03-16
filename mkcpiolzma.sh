#!/bin/bash

if test $(whoami) != "root"; then
    sudo $0
    exit
fi

PATH=~jcard/Desktop/buildroot-2009.08/bin:$PATH
BRDIR=~jcard/Desktop/buildroot-2009.08-build-2

cd ${BRDIR}/binaries/dns323

if ! test -d tmp; then
	mkdir tmp
fi

sudo mount -o loop rootfs.arm.ext2 tmp
cd tmp
#find . | cpio --quiet -o -H newc | lzma -9 > ../rootfs.arm.cpio.lzma
find . | cpio --quiet -o -H newc | lzma e -si -so > ../rootfs.arm.cpio.lzma
cd ..
sudo umount tmp
chown jcard:users rootfs.arm.cpio.lzma

