#!/bin/bash

check() {
	if test "$1" != 0; then
		echo -e "\nFirmware creation FAILED at $2, exiting."
		exit 1
	fi
}

if test "$(dirname $0)" != "."; then
	echo "This script must be run in the root of the tree, exiting."
	exit 1
fi

if test -z "$BLDDIR"; then
	cat<<-EOF
		Set the environment variable BLDDIR to the build directory, e.g
		   export BLDDIR=<path to where you which the build dir>\nkeep it out of this tree."
		exiting.
	EOF
	exit 1
fi

case $1 in
	sqmtd) rootfs="rootfs.arm.sqmtd" ;;
	sqfs) rootfs="rootfs.arm.cpio-sq.lzma" ;;
	gz) rootfs="rootfs.arm.cpio.gz" ;;
	lzma) rootfs="rootfs.arm.cpio.lzma" ;;
	*)	echo "Usage: mkfw gz | lzma | sqfs | sqmtd"
		exit
		;;
esac

# max sizes, dns323-fw checks them:
# kernel <= 1572800 + 64, initramfs <= 6488000 + 64
MAXK=1572800
MAXFS=6488000

PATH=$(pwd)/bin:$PATH
DESTD=$BLDDIR/binaries/dns323
#KVER=$(awk '/version:/{print $5}' $BLDDIR/project_build_arm/dns323/root/boot/linux*.config)
KVER=$(cat $BLDDIR/project_build_arm/dns323/.linux-version)
VER=$(cut -f2 -d" " customroot/etc/Alt-F)

if ! test -f ${DESTD}/zImage -a -f ${DESTD}/$rootfs; then
	echo "${DESTD}/zImage or ${DESTD}/$rootfs not found, exiting"
	exit 1
fi

if test ${DESTD}/rootfs.arm.ext2 -nt ${DESTD}/$rootfs; then
	echo "${DESTD}/rootfs.arm.ext2 is newer than ${DESTD}/$rootfs,  exiting"
	exit 1
fi

# change machine ID
devio > ${DESTD}/tImage 'wl 0xe3a01c06,4' 'wl 0xe3811006,4'
check $? devio

cat ${DESTD}/zImage >> ${DESTD}/tImage

# create kernel uboot image
mkimage -A arm -O linux -T kernel -C none \
	-e 0x00008000 -a 0x00008000 \
	-n "Alt-F-${VER}, kernel ${KVER}" -d ${DESTD}/tImage ${DESTD}/uImage
check $? "kernel mkimage"

# create initramfs uboot image
mkimage -A arm -O linux -T ramdisk -C none \
	-e 0x00800000 -a 0x00800000 \
	-n "Alt-F-${VER}, initrd" -d ${DESTD}/$rootfs \
	${DESTD}/urootfs
check $? "initramfs mkimage"

# Model	product_id	custom_id	model_id	sub_id	NewVersion type
# DNS321		a		1			1			2		1		1
# DNS323		7		1			1			1		4		0
# CH3SNAS		7		2			1			1		4		0
# DUO 35-LR		7		3			1			1		4		0
# Alt-F-0.1B	1		2			3			4		5		0
# Alt-F-0.1RC	7		1			1			1		4		0

name=(DNS-321 DNS-323 Conceptronics-CH3SNAS Fujitsu-Siemens-DUO-35-LR)
prod=(10 7 7 7)
cust=(1 1 2 3)
model=(1 1 1 1)
sub=(2 1 1 1)
nver=(1 4 4 4)
type=(1 0 0 0)

num=${#name[*]}
if test $num != ${#prod[*]} -o $num != ${#cust[*]} -o $num != ${#cust[*]} \
	-o $num != ${#model[*]} -o $num != ${#sub[*]} -o $num != ${#nver[*]} 
	-o $num != ${#type[*]}; then
		check 1 "firmware descriptions"
fi

for i in $(seq 0 $((num-1))); do
	# merge kernel and initramfs
	echo -e "\n___ ${name[i]} ___"
	dns323-fw -m -p ${prod[i]} -c ${cust[i]} -l ${model[i]} \
		-u ${sub[i]} -v ${nver[i]} -t ${type[i]} \
		-k ${DESTD}/uImage -i ${DESTD}/urootfs ${DESTD}/Alt-F-${VER}-${name[i]}.bin
	check $? merging

	# verification, check that splitint the created fw works fine
	err=$(dns323-fw -s ${DESTD}/Alt-F-${VER}-${name[i]}.bin)
	check $? "split, err:\n$err\n"

	# paranoic, verify that the splited components equal the originals
	cmp kernel ${DESTD}/uImage
	check $? "paranoic kernel"

	cmp initramfs ${DESTD}/urootfs
	check $? "paranoic initramfs"
done

# report kernel and initramfs available flash space
echo
echo Available kernel flash space: $(expr $MAXK - $(stat --format=%s kernel)) bytes
echo Available initramfs flash space: $(expr $MAXFS - $(stat --format=%s initramfs)) bytes

rm kernel initramfs defaults ${DESTD}/urootfs ${DESTD}/uImage ${DESTD}/tImage
