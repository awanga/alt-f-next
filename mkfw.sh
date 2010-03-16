#!/bin/bash

PATH=~jcard/Desktop/buildroot-2009.08/bin:$PATH

DESTD=~jcard/Desktop/buildroot-2009.08-build-2/binaries/dns323/
KVER=2.6.32.1
VER=0.1-B1

devio > ${DESTD}/tImage 'wl 0xe3a01c06,4' 'wl 0xe3811006,4'
cat ${DESTD}/zImage >> ${DESTD}/tImage

mkimage -A arm -O linux -T kernel -C none \
	-e 0x00008000 -a 0x00008000 \
	-n "Alt-F ${VER}, kernel ${KVER}" -d ${DESTD}/tImage ${DESTD}/uImage

rm ${DESTD}/tImage

mkimage -A arm -O linux -T ramdisk -C none \
	-e 0x00800000 -a 0x00800000 \
	-n "Alt-F ${VER}, initramfs" -d ${DESTD}/rootfs.arm.cpio-sq.lzma \
	${DESTD}/urootfs.arm.cpio-sq.lzma

dns323-fw -m -k ${DESTD}/uImage -i ${DESTD}/urootfs.arm.cpio-sq.lzma \
	${DESTD}/Alt-F-0.1B1.bin

rm ${DESTD}/urootfs.arm.cpio-sq.lzma ${DESTD}/uImage
chown jcard:users ${DESTD}/Alt-F-0.1B1.bin
chmod a+r ${DESTD}/Alt-F-0.1B1.bin

#dns323-fw -m [-q (quiet)] -k kernel_file -i initramfs_file
#        [-d defaults_file] [-p product_id]  [-c custom_id] [-l model_id ]
#        [-u sub_id] [-v new_version] firmware_file

