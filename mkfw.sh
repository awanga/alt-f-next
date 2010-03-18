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

PATH=$(pwd)/bin:$PATH
DESTD=$BLDDIR/binaries/dns323/
KVER=2.6.33.1
VER=0.1B1

devio > ${DESTD}/tImage 'wl 0xe3a01c06,4' 'wl 0xe3811006,4'
cat ${DESTD}/zImage >> ${DESTD}/tImage

mkimage -A arm -O linux -T kernel -C none \
	-e 0x00008000 -a 0x00008000 \
	-n "Alt-F-${VER}, kernel ${KVER}" -d ${DESTD}/tImage ${DESTD}/uImage

rm ${DESTD}/tImage

mkimage -A arm -O linux -T ramdisk -C none \
	-e 0x00800000 -a 0x00800000 \
	-n "Alt-F-${VER}, initramfs" -d ${DESTD}/rootfs.arm.cpio-sq.lzma \
	${DESTD}/urootfs.arm.cpio-sq.lzma

dns323-fw -m -k ${DESTD}/uImage -i ${DESTD}/urootfs.arm.cpio-sq.lzma \
	${DESTD}/Alt-F-0.1B1.bin

rm ${DESTD}/urootfs.arm.cpio-sq.lzma ${DESTD}/uImage

#dns323-fw -m [-q (quiet)] -k kernel_file -i initramfs_file
#        [-d defaults_file] [-p product_id]  [-c custom_id] [-l model_id ]
#        [-u sub_id] [-v new_version] firmware_file

