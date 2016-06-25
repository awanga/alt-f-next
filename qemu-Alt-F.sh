#!/bin/sh

# This emulates Alt-F on you computer using qemu, simulating a box with
# a Versatile PB arm board
#
# You have to install qemu-system-arm on your computer. It works for me
# on a linux machine, and it might as well works under MS-Windows
# You only have to download 'qemu-Alt-F.sh' and execute it.
#
# A folder named ~/qemu-Alt-F will be created for you and this script
# makes all needed downloads and starts the qemu emulation
#
# Three 10/10/5GB virtual disks are created and you can use them as
# normal disks, with its contents being persistent across reboots.
# Flash memory ias also emulated and "settings" can be saved and are also
# persistent across reboots.
#
# All networking is firewalled except for ports 80 and 22,
# which are forwarded to your computer's 5555 and 5556 ports,
#
# So you can type http://localhost:5555 on your computer browser to have
# acess to the Alt-F webUI, or use 'ssh -p 5556 root@localhost' (after
# setting the root password using the webUI)
#
# Serial console is enabled for root, no password, you can use 'CTRL+a c'
# to switch between the qemu monitor (use 'quit' to exit qemu) and the
# Alt-F console and vice-versa, see http://wiki.qemu.org/download/qemu-doc.html#Keys
#
# The following error is expected and is harmless, as there is no
# emulation for fan/temperature/buttons/etc:
# sysctrl: Hardware board qemu not supported, exiting

DSITE="http://downloads.sourceforge.net/project/alt-f/Releases/0.1RC5/Simulator"
ADIR="$HOME/qemu-Alt-F"

if ! which qemu-img > /dev/null 2>&1; then
	echo "qemu-img not found, you have to install it, exiting."
	exit 1
fi

if ! which qemu-system-arm > /dev/null 2>&1; then
	echo "qemu-system-arm not found, you have to install it, exiting."
	exit 1
fi

if ! test -d "$ADIR"; then
	if ! mkdir "$ADIR"; then
		echo "Couldn't create "$ADIR", exiting."
		exit 1
	else
		echo "Created "$ADIR", where disk, kernel and rootfs images will be stored."
		sleep 5
	fi
fi

cd ~/qemu-Alt-F

# create disks
if ! test -f qemu-disk-left.img; then qemu-img create -f qcow2 qemu-disk-left.img 10G; fi
if ! test -f qemu-disk-right.img; then qemu-img create -f qcow2 qemu-disk-right.img 10G; fi
if ! test -f qemu-disk-usb.img; then qemu-img create -f qcow2 qemu-disk-usb.img 5G; fi
if ! test -f qemu-flash.img; then qemu-img create -f raw qemu-flash.img 64M; fi

# download kernel and rootfs image
if ! test -f qemu-zImage; then wget $DSITE/qemu-zImage; fi
if ! test -f qemu-rootfs.arm.sqall.xz; then wget $DSITE/qemu-rootfs.arm.sqall.xz; fi

MEM=128 # MB

QEMU_AUDIO_DRV=none qemu-system-arm \
-machine versatilepb -m $MEM \
-serial mon:stdio -nographic \
-kernel qemu-zImage \
-initrd qemu-rootfs.arm.sqall.xz \
-hda qemu-disk-left.img \
-hdb qemu-disk-right.img \
-hdc qemu-disk-usb.img \
-pflash qemu-flash.img \
-netdev user,id=eth0 -device e1000,netdev=eth0 \
-redir tcp:5555::80 \
-redir tcp:5556::22
