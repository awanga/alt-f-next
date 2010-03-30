
You know that you don't need to build Alt-F, don't you? you can just download and install it. If building is what you really need, then read on.

This source tree is a modified buildroot source tree
(http://buildroot.uclibc.org buildroot-2009.08), resulting of my changes
and fighting with buildroot. Instead of distributing a patch against, I
decided to re-distribute the whole tree with my changes. IT IS NOT A
FORK. I latter intend to use a more recent buildroot version.

The files you might be interested in are in the customroot directory, the
mk*.sh scripts, the package/Alt-F-utils directory, the host-tools
directory and the patches directory.

If you really want to try to build Alt-F, you must choose to checkout the current
developement tree, unstable, or a stable release.
To checkout the developement tree, do:

	svn checkout http://alt-f.googlecode.com/svn/trunk/alt-f alt-f-read-only

to see what stable releases are available, do:

	svn list https://alt-f.googlecode.com/svn/tags

and checkout the one of your choice, e.g.

	svn checkout http://alt-f.googlecode.com/svn/tags/Release-0.1B1 alt-f-read-only

Then,
  
  cd alt-f-read-only
  export BLDDIR=<dir> # where you want the build tree, e.g. ~/Alt-F-build
  ./mkprepare.sh
  make O=$BLDDIR

and go for a two hours walk (old P4HT@3.2GHz/2GB) 

When finished, you should find in $BLDDIR/binaries/dns323, the kernel,
zImage, and the root filesystem image, rootfs.arm.ext2.

Some mk*.sh scripts will ask for the root password; this is needed to
mount the generated ext2 rootfs as a loop device and manipulate it.
See the source.

To create an initramfs, do
  ./mkinitramfs.sh sqfs

and you will find the initramfs in $BLDDIR/binaries/dns323,
rootfs.arm.cpio-sq.lzma, that you can use together with zImage and fonz
"reloaded" to boot the new kernel. The kernel cmdline is simply
"console=ttyS0,115200".
The initramfs is a cpio lzma compressed initramfs, where the /usr directory
was squashfs-4 compressed with lzma, resulting in the file usr.squashfs.

The mkinitramfs.sh script also accepts other arguments, "gz" for a gziped
cpio initramfs, faster to create and boot but using too much memory at runtime,
or "lzma", that crates a lzma compressed cpio initramfs, smaller in size but
slower to boot.

To create a "reloaded" tar file, just
	./mkreloaded.sh

and you will find it in $BLDDIR/binaries/dns323/Alt-F-0.1B1.tar, not compressed.
It makes no sense to compress it, because it is already internally compressed.

To create a firware image, just type
	./mkfw.sh

and again in $BLDDIR/binaries/dns323 you will found Alt-F-0.1B1.bin, file that
you can use to flash Alt-F using Alt-F firmware updater web page.
READ THE BIG RED WARNING BEFORE DOING IT.

The firmware file can't deliberately be flashed using the vendors web
page firmware updater. You have to experiment and try Alt-F before
deciding to flash it. You can however tune the mkfw.sh script to
generate a firmware file accepted by the vendors web page.

The Alt-F firmware updater web page also accepts vendor distributed
firmware, so you can revert the box back to its original state.

Other buildroot make options:

make O=<path-to-build-directory> menuconfig # to configure the build
make O=<path-to-build-directory> linux26-menuconfig # to fine configure linux
make O=<path-to-build-directory> busybox-menuconfig # to fine configure busybox
make O=<path-to-build-directory> uclibc-menuconfig  # to fine configure uclibc
make O=<path-to-build-directory> saveconfig  # to save configuration (in local/dns323)
make O=<path-to-build-directory> loadconfig # to retrieve the saved configuration

Buildroot is temperamental, to say the least. After you do a "make", you
should do a second one :-/, at least in the first build or when
configuration files are changed.

"make clean" does not do what you would expect. The official way of
cleaning is to delete the build tree and restart again :-/.

A faster, non guaranteed and involved way:
  rm $BLDDIR/project_build_arm/dns323/autotools-stamps/*
  rm -rf $BLDDIR/project_build_arm/dns323/root
  rm $BLDDIR/project_build_arm/dns323/.root
  make O=$BLDDIR

This way the toolchain, kernel, and already built packages are not
rebuilt, only the root directory is repopulated and the rootfs rebuild.

