#!/bin/bash

if test $(whoami) != "root"; then
    sudo $0 $*
    exit
fi

PATH=~jcard/Desktop/buildroot-2009.08/bin/:$PATH
BRDIR=~jcard/Desktop/buildroot-2009.08-build-2

cd ${BRDIR}/binaries/dns323

if ! test -d tmp; then
	mkdir tmp
fi

if test "$1" = "all"; then

  mount -o loop rootfs.arm.ext2 tmp
  mksquashfs tmp/ rootfs.arm.squashfs -comp lzma -noappend
  umount tmp

else #only usr

  cp rootfs.arm.ext2 rootfs.arm.ext2.safe
  mount -o loop rootfs.arm.ext2 tmp
  # block sizes: 131072 262144 524288 1048576
  mksquashfs tmp/usr/ usr.squashfs -comp lzma -b 262144 \
	-always-use-fragments -keep-as-directory
  rm -rf tmp/usr/*
  mv usr.squashfs tmp
  cd tmp
#  find . | cpio --quiet -o -H newc | gzip -9 > ../rootfs.arm.cpio-sq.gz
  find . | cpio --quiet -o -H newc | lzma e -si -so  > ../rootfs.arm.cpio-sq.lzma
  cd ..
  umount tmp
  mv rootfs.arm.ext2.safe rootfs.arm.ext2

fi

chown jcard:users *
