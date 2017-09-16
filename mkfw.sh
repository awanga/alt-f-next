#!/bin/bash

check() {
	if test "$1" != 0; then
		echo -e "\nmkfw: Firmware creation FAILED at $2, exiting."
		exit 1
	fi
}

usage() {
	echo "Usage: mkfw [type] (cpio|squsr|sqall*|sqsplit) [compression] (gz|lzma|xz*)"
	exit 1
}

if test "$(dirname $0)" != "."; then
	echo "mkfw: This script must be run in the root of the tree, exiting."
	exit 1
fi

if test -z "$BLDDIR"; then
	echo "mkfw: Run '. exports [board]' first."
	exit 1
fi

if test "$#" = 0; then
	TYPE=sqall
	COMP=xz
elif test "$#" = 1; then
	if test "$1" = "cpio" -o "$1" = "squsr" -o "$1" = "sqall" -o "$1" = "sqsplit"; then
		TYPE=$1
		COMP=xz
	elif test "$1" = "gz" -o "$1" = "lzma" -o "$1" = "xz"; then
		TYPE=cpio
		COMP=$1
	else
		usage
	fi
elif test "$#" = 2; then
	TYPE=$1
	COMP=$2
else
	usage
fi

if test $TYPE != "cpio" -a $TYPE != "squsr" -a $TYPE != "sqall" -a $TYPE != "sqsplit" \
	-a $COMP != "gz" -a $COMP != "lzma" -a $COMP != "xz"; then
	usage
fi

. .config 2> /dev/null
board=$BR2_PROJECT

if test $# = 0 -a \( "$board" = "dns325" -o "$board" = "dns327" \); then
	TYPE="sqsplit"
	COMP=xz
fi

if test $TYPE = "sqsplit" -a "$board" != "dns325" -a "$board" != "dns327"; then
	echo "mkfw: ERROR, \"sqsplit\" is only for a dns-320/325/327"
	exit 1
fi

rootfs=rootfs.arm.$TYPE.$COMP
if test $TYPE = "sqsplit"; then
	rootfs=rootfs.arm.sqall.$COMP
	sqimage=rootfs.arm.sqimage.$COMP
fi

TFTPD=/srv/tftpboot # for development using tftp on u-boot using serial adapter
DESTD=$BLDDIR/binaries/$board
KVER=$(cat $BLDDIR/project_build_arm/$board/.linux-version)
VER=$(cut -f2 -d" " customroot/etc/Alt-F)

if ! test -f ${DESTD}/zImage -a -f ${DESTD}/$rootfs; then
	echo "mkfw: ${DESTD}/zImage or ${DESTD}/$rootfs not found, exiting"
	exit 1
fi

if test ${DESTD}/rootfs.arm.ext2 -nt ${DESTD}/$rootfs; then
	echo "mkfw: ${DESTD}/rootfs.arm.ext2 is newer than ${DESTD}/$rootfs,  exiting"
	exit 1
fi

if test -n "$sqimage"; then
	if ! test -f "${DESTD}/$sqimage"; then
		echo "mkfw: ${DESTD}/$sqimage not found, exiting"
		exit 1
	fi

	if test "${DESTD}/$rootfs" -nt "${DESTD}/$sqimage"; then
		echo "mkfw: ${DESTD}/$rootfs is newer than ${DESTD}/$sqimage,  exiting"
		exit 1
	fi
	
	# prepend to sqimage its size and md5sum so that one can know it at boot using nanddump in rcS
	MTD_PAGES=2048 # NAND flash page size
	if test "${DESTD}/$sqimage" -nt "${DESTD}/tsqimage"; then
		len=$(stat -c %s "${DESTD}/$sqimage")
		md5s=$(md5sum "${DESTD}/$sqimage" | awk '{print $1}')
		echo "sqimage_size=$len; sqimage_md5s=$md5s;" | dd bs=$MTD_PAGES conv=sync > "$DESTD/tsqimage"
		cat "${DESTD}/$sqimage" >> "${DESTD}/tsqimage"
	fi
	sqimage=tsqimage
fi

case $board in
	dns323) ;;
	dns325|dns327) sq_opts="-a ${DESTD}/$sqimage" ;;
	*) echo "mkfw: Unsupported \"$board\" board"; exit 1;;
esac

# the several vendors firmware signatures:
# Model	product_id	custom_id	model_id	sub_id	NewVersion type
# DNS323		7		1			1			1		4		0
# CH3SNAS		7		2			1			1		4		0
# DUO35-LR		7		3			1			1		4		0
# DNS321-A		a		1			1			1/2		0/1		1
# DNS343		9		1			1			1/2		1		2
# DNS325-A		0		8			5			1/2		0		3
# DNS320-A		0		8			7			1/2		0		4
# DNS320-B		0		8			c			1		1		5
# DNS320L		0		8			b			1		1		6
# Alt-F-0.1B	1		2			3			4		5		0
# Alt-F-0.1RC	7		1			1			1		4		0

# FIXME: use associative arrays
# the brand models
name=(DNS-323-rev-AxBxCx CH3SNAS DUO-35LR DNS-321-rev-Ax DNS-343 DNS-325-rev-Ax DNS-320-rev-Ax DNS-320-rev-Bx DNS-320L-rev-Ax DNS-327L-rev-Ax)
working=(y y y y n y y y y y)

# the buildroot boards .config used
# better call it arch: orion (dns321/323), kirkwood(dns320/320L/325), armada-370(dns-327L)
hwboard=(dns323 dns323 dns323 dns323 dns343 dns325 dns325 dns325 dns325 dns327)

# the firmware file signatures
prod=( 7 7 7 10 9 0 0  0  0 0)
cust=( 1 2 3  1 1 8 8  8  8 8)
model=(1 1 1  1 1 5 7 12 11 13)
sub=(  1 1 1  2 2 2 2  1  1 1)
nver=( 4 4 4  1 1 0 0  1  1 1)
type=( 0 0 0  1 2 3 4  5  6 7)

# the amount of NAND flash bytes that u-boot copies to ram at bootm for each board
# read the NOTE-2 bellow)
kernel_max=(1572864 1572864 1572864 1572864 1572864 3145728 3145728 3145728 3145728 3145728)
initramfs_max=(6488064 6488064 6488064 10485760 14417920 3145728 3145728 3145728 3145728 4194304)
sqimage_max=(0 0 0 0 0 106954752 106954752 104857600 104857600 81788928)

# some kernels need a prologue to change the device_id set by the bootloader
# read NOTE-1 bellow
#prez=(0606 0606 0606 0606 0606  "" ""  128a 128a)
prez=(0606 0606 0606 0606 0606  "" "" "" "" "")

DTSDIR=${KERNEL}/arch/arm/boot/dts
# other kernels needs an epilogue with a hardware device tree description
#postz=("" "" "" "" "" kirkwood-dns325.dtb kirkwood-dns320.dtb "" "")
postz=("" "" "" "" "" kirkwood-dns325.dtb kirkwood-dns320-a.dtb kirkwood-dns320-b.dtb kirkwood-dns320l.dtb armada-370-dlink-dns327l.dtb)

# NOTE-1: DNS-323/DNS-321:
# Sets the cpu r1 to the machine ID, overriding the value that u-boot sets there.
# This is necessary because D-Link uses a wrong mach-type (=526, a ARCH_MV88fxx81)
# in their bootloader, which sets r1 to 526; the correct linux mach-id for the machine,
# according to 'arch/arm/tools/mach-types' is 1542 (0x0606). 
#
# The bellow 'devio' command writes '06 1c a0 e3 06 10 81 e3' to the tImage start, 
#	devio 'wl 0xe3a01c06,4' 'wl 0xe3811006,4'
# which 'arm-linux-objdump -b binary -m armv5te -D tImage' dissasembles as:
#
#   0:   e3a01c06        mov     r1, #1536       ; 0x600
#   4:   e3811006        orr     r1, r1, #6      ; 0x6
#
# this adds MSB (1st instruction) to LSB (2nd instruction): 0x0600 + 0x06 (1536 + 6 = 1542)
#
# DNS-325/DNS320:
# u-boot passes 0x020f as mach-id: (after setting CONFIG_DEBUG_LL enabled:
# make menuconfig", "Kernel hacking", "Kernel low-level debugging functions")
#
# Error: unrecognized/unsupported machine ID (r1 = 0x0000020f).
# Available machine support: (after patching arch/arm/tools/mach-types) 
# 
# ID (hex)	(dec) NAME
# 00000ed8	3800  D-Link DNS-325
# 00000f91	3985  D-Link DNS-320
#
# devio 'wl 0xe3a01c0e,4' 'wl 0xe38110d8,4' (0x0e00 + 0xd8)
# devio 'wl 0xe3a01c0f,4' 'wl 0xe3811091,4' (0x0f00 + 0x91)
#
# for the DNS-325, instead of the above 'devio' stuff, append the dts to the kernel_max
#
# DNS-320L: mach_id is 4746 (0x128A)
# devio 'wl 0xe3a01c12,4' 'wl 0xe381108a,4' (0x1200 + 0x8a)

# NOTE-2: about kernel_max/initramfs_max above for the DNS-325:
#
# although the DNS-325 has 5MB flash partition for the kernel and rootfs,
# u-boot only copies 0x300000 (3145728d) bytes from flash to memory, leading to a 
# "Verifying Checksum ... Bad Data CRC" error at boot,see u-boot environment variable:
# bootcmd=nand read.e 0xa00000 0x100000 0x300000;nand read.e 0xf00000 0x600000 0x300000;bootm 0xa00000 0xf00000
#
# NAND read: device 0 offset 0x100000, size 0x300000
# load addr ....  =a00000
#
# NAND read: device 0 offset 0x600000, size 0x300000
# load addr ....  =f00000
# 3145728 bytes read: OK
#
# One could use fw_printenv/fw_setenv from u-boot/tools/env to fix that, while *still*
# running the stock firmware and *before* flashing bigger kernel/rootfs, 
# but most users would miss that (users just don't read README files)

num=${#name[*]}
if test $num != ${#prod[*]} -o $num != ${#cust[*]} -o $num != ${#cust[*]} \
	-o $num != ${#model[*]} -o $num != ${#sub[*]} -o $num != ${#nver[*]} \
	-o $num != ${#type[*]} -o $num != ${#hwboard[*]} -o $num != ${#kernel_max[*]} \
	-o $num != ${#initramfs_max[*]} -o $num != ${#prez[*]} -o $num != ${#postz[*]}; then
		check 1 "firmware descriptions"
fi

# create initramfs uboot image
mkimage -A arm -O linux -T ramdisk -C none \
	-e 0x00800000 -a 0x00800000 \
	-n "Alt-F-${VER}, initrd" -d ${DESTD}/$rootfs \
	${DESTD}/urootfs
check $? "initramfs mkimage"
echo

for i in ${!name[*]}; do
	if ! test "$board" = "${hwboard[i]}" -a "${working[i]}" = "y"; then continue; fi

	# build prologue
	if test -n "${prez[i]}" -a ! -f ${DESTD}/${prez[i]}; then
		#devio 'wl 0xe3a01c06,4' 'wl 0xe3811006,4' > ${DESTD}/${prez[i]}
		MSB=${prez[i]:0:2}; LSB=${prez[i]:2:2}
		devio "wl 0xe3a01c${MSB},4" "wl 0xe38110${LSB},4" > ${DESTD}/${prez[i]}
		check $? devio
		rm -f ${DESTD}/tImage
	fi

	# build epilogue
	if test -n "${postz[i]}" -a \( ! -f ${DESTD}/${postz[i]} -o \
			$DTSDIR/$(basename ${postz[i]} .dtb).dts -nt $DESTD/${postz[i]} \); then
		if test -z "$KERNEL"; then
			echo "mkfw: Error, execute '. exports' first."
			exit 1
		fi

		make -C ${KERNEL} ARCH=arm CROSS_COMPILE=arm-linux- ${postz[i]}
		check $? dts
		cp $DTSDIR/${postz[i]} ${DESTD}/
		rm -f ${DESTD}/tImage
	fi

	# prepend/postpend prologue and epilogue to kernel (not both!)
	if test -n "${prez[i]}"; then
		cat ${DESTD}/${prez[i]} ${DESTD}/zImage > ${DESTD}/tImage
	elif test -n "${postz[i]}"; then
		cat ${DESTD}/zImage ${DESTD}/${postz[i]} > ${DESTD}/tImage
	fi

	echo -e "\n___ ${name[i]} ___"

	# create kernel uboot image
	mkimage -A arm -O linux -T kernel -C none \
		-e 0x00008000 -a 0x00008000 \
		-n "Alt-F-${VER}, kernel ${KVER}" -d ${DESTD}/tImage ${DESTD}/uImage
	check $? "kernel mkimage"

	# check sizes, see comment bellow
	len=$(expr $(stat -c %s "${DESTD}/uImage") - ${kernel_max[i]})
	if test $len -gt 0; then
		check 1 "kernel too big by $len bytes, max is ${kernel_max[i]}"
	fi
	len=$(expr $(stat -c %s "${DESTD}/urootfs") - ${initramfs_max[i]})
	if test $len -gt 0; then
		check 1 "rootfs too big by $len bytes, max is ${initramfs_max[i]}"
	fi
	if test -n "$sq_opts"; then
		len=$(expr $(stat -c %s "${DESTD}/$sqimage") - ${sqimage_max[i]})
		if test $len -gt 0; then
			check 1 "sqimage too big by $len, max is ${sqimage_max[i]}"
		fi
	fi

	# merge kernel and initramfs (notice that dns323-fw only validates flash partitions sizes, not u-boot load limits)
	dns323-fw -m -p ${prod[i]} -c ${cust[i]} -l ${model[i]} \
		-u ${sub[i]} -v ${nver[i]} -t ${type[i]} \
		-k ${DESTD}/uImage -i ${DESTD}/urootfs $sq_opts ${DESTD}/Alt-F-${VER}-${name[i]}.bin
	check $? "merging (max: ${kernel_max[i]}/${initramfs_max[i]}/${sqimage_max[i]})"

	# generate SHA1
	(cd ${DESTD}; sha1sum Alt-F-${VER}-${name[i]}.bin > Alt-F-${VER}-${name[i]}.sha1)

	# verification, check that spliting the created fw works fine
	err=$(dns323-fw -s ${DESTD}/Alt-F-${VER}-${name[i]}.bin)
	check $? "split, err:\n$err\n"

	# paranoic, verify that the splited components equal the originals
	cmp kernel ${DESTD}/uImage
	check $? "cmp kernel"

	err=$(mkimage -l kernel 2>&1)
	check $? "mkimage check: $err"

	cmp initramfs ${DESTD}/urootfs
	check $? "cmp initramfs"

	err=$(mkimage -l initramfs 2>&1)
	check $? "mkimage check: $err"

	if test -n "$sq_opts"; then
		cmp sqimage ${DESTD}/$sqimage
		check $? "cmp sqimage"
	fi

	# report kernel and initramfs available flash space
	echo
	echo Available kernel flash space: $(expr ${kernel_max[i]} - $(stat -c %s kernel)) bytes
	echo Available initramfs flash space: $(expr ${initramfs_max[i]} - $(stat -c %s initramfs)) bytes

	(cd ${DESTD}; cp uImage $TFTPD/uImage-${name[i]})

done

(
	cd ${DESTD};
	cp urootfs $TFTPD/urootfs-$board
	if test "$board" = dns325 -o "$board" = dns327; then
		cp rootfs.arm.sqimage.xz $TFTPD/rootfs.arm.sqimage.xz-$board
	fi
)

if ! test -d $TFTPD -a -w $TFTPD; then echo "WARNING: tftp folder non existing or writable. Only useful for users with serial adapter on the box and using u-boot."; fi

rm -f kernel initramfs defaults \
	${DESTD}/urootfs ${DESTD}/uImage ${DESTD}/tImage ${DESTD}/tsqimage
