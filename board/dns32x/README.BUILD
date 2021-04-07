Quick Instructions for Alf-F. For the full documentation read the Wiki.

Checkout the development tree:

	git clone http://github.com/awanga/alt-f-next -b next

Then,
  
	cd alt-f-next			# change to the checkout directory
	make alt-f_{board}_defconfig	# setup configuration
	make >& build.log		# make it all, logging to build.log

When finished, you should find:

-in $BINARIES, the kernel, "zImage", the root filesystem image, "rootfs.arm.*",
 and the firmware files, "Alt-F-<version>-<model>.bin"
-in $ROOTFS you will find the directory structure used to create the
 root filesystem image, "rootfs.arm.*".
-in $KERNEL the built linux kernel

To build alt-f packages:

	make alt-f_base_defconfig	# base (armv5) config for packages
	./board/dns32x/build_pkgs.sh	# script to automatically build pkgs

When finished, you should find:

-in output/pkgs folder, the packake binaries and ipkg package index
