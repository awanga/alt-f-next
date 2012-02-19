#summary How to Build

=How to Build=

{{{

You know that you don't need to build Alt-F, don't you? you can just
download and install it. If building is what you really need, then read
on.

This source tree is a modified buildroot source tree
(http://buildroot.uclibc.org buildroot-2009.08), resulting of my changes
and fighting with buildroot. Instead of distributing a patch against, I
decided to re-distribute the whole tree with my changes. IT IS NOT A
FORK. I latter intend to use a more recent buildroot version.

The files you might be interested in are in the customroot directory,
the mk*.sh scripts, the package/Alt-F-utils directory, and the host-tools
directory.

If you really want to try to build Alt-F, you must choose to checkout
the current development tree, unstable, or a stable release.

To checkout the development tree, do:

	svn checkout http://alt-f.googlecode.com/svn/trunk/alt-f alt-f-read-only

to see what stable releases are available, do:

	svn list https://alt-f.googlecode.com/svn/tags

and checkout the one of your choice, e.g.

	svn checkout http://alt-f.googlecode.com/svn/tags/Release-0.1B1 alt-f-read-only

Then,
  
	cd alt-f-read-only/alt-f
	export BLDDIR=<dir> # where you want the build tree, e.g. ~/Alt-F-build
	export PATH=$PATH:$PWD/bin:$BLDDIR/build_arm/staging_dir/usr/bin: # PATH to host-tools and build made programs
	./mkprepare.sh # build host-tools, put them in bin/
	make O=$BLDDIR menuconfig # exit without making modifications (but save if asked)
	make O=$BLDDIR

and make a 15 minutes coffee-break (Core i5-2400@3.10GHz/4GB), or go for a two hours walk (old P4HT@3.2GHz/2GB) (times given does not include tarball downloads)

	make O=$BLDDIR # for the *first* build a second (faster) make is needed

When finished, you should find in $BLDDIR/binaries/dns323, the kernel,
"zImage", and the root filesystem image, "rootfs.arm.ext2".

In $BLDDIR/project_build_arm/dns323/root/ you will find the directory
structure used to create the root filesystem image, "rootfs.arm.ext2".
That directory was first populated by buildroot, using first the
contents of target/generic/target_busybox_skeleton as a template, and
then populating it with the configured packages; after that the
directory is processed by the "configfs" script, that copied the
contents of "customroot" to it and also remove some other files.

To create an initramfs, do
	./mkinitramfs.sh <sqfs|gz|lzma>

Some mk*.sh scripts will ask for the root password; this is needed to
mount the generated ext2 rootfs as a loop device and manipulate it. See
the source.

mkinitramfs.sh created the initramfs in $BLDDIR/binaries/dns323,
"rootfs.arm.cpio-sq.lzma", that you can use together with "zImage" and
fonz "reloaded" to boot the new kernel.
The kernel cmdline is simply "console=ttyS0,115200". You can use other
kernel recognized options, and also some Alt-F recognized options such
as "initdbg", that opens a shell for you on the serial console before
"init" being run and "nodef", disabling the reading of flash-saved
default settings.

The initramfs is a cpio lzma compressed initramfs, where the /usr
directory was squashfs-4 compressed with lzma, resulting in the file
usr.squashfs.

The mkinitramfs.sh script also accepts other arguments, "gz" for a
gziped cpio initramfs, faster to create and boot but using too much
memory at runtime, or "lzma", that crates a lzma compressed cpio
initramfs, still smaller in size but slower to boot.

If you are already using Alt-F, you can copy zImage and
rootfs.arm.cpio-sq.lzma (or rootfs.arm.cpio.gz or rootfs.arm.cpio.lzma)
to the box "/root" directory and issue a "reboot" command.
The /etc/init.d/rcE script will recognize these files and will
do a kexec after doing all other cleanup, thus reloading a new kernel
and initramfs without an actual hardware reboot.

To create a "reloaded" tar file, just
	./mkreloaded.sh <sqfs|gz|lzma>

and you will find it in $BLDDIR/binaries/dns323/Alt-F-0.1B1.tar.
It is not compressed as it makes no sense to compress it (it is already
internally compressed).

To create a firmware image, just type
	./mkfw.sh <sqfs|gz|lzma>

and again in $BLDDIR/binaries/dns323 you will found "Alt-F-0.1B1.bin",
file that you can use to flash Alt-F using Alt-F firmware updater web
page. READ THE BIG RED WARNING BEFORE DOING IT. YOU HAVE BEEN WARNED.

The firmware file can't deliberately be flashed using the vendors web
page firmware updater. You have to experiment and try Alt-F before
deciding to flash it. You can however edit the mkfw.sh script to
generate a firmware file accepted by the vendors web page.

The Alt-F firmware updater web page also accepts vendor distributed
firmware, so you can revert the box back to its original state.

Other buildroot make options:
============================

make O=$BLDDIR menuconfig # to configure the build
make O=$BLDDIR linux26-menuconfig # to fine configure linux
make O=$BLDDIR busybox-menuconfig # to fine configure busybox
make O=$BLDDIR uclibc-menuconfig  # to fine configure uclibc
make O=$BLDDIR saveconfig  # to save configuration (in local/dns323/)
make O=$BLDDIR loadconfig # to retrieve the saved configuration

Make clean
==========

"make clean" does not do what you would expect. The official way of
cleaning is to delete the build tree and restart again :-/.

A faster, *non guaranteed* way to clean, that sometimes produces erroneous system
libraries is:

  rm $BLDDIR/project_build_arm/dns323/autotools-stamps/* # but *not* the gcc_libs_target_installed file
  rm -rf $BLDDIR/project_build_arm/dns323/root/* # but *not* the lib directory
   nor the usr/lib/libstdc++.so* files
  rm $BLDDIR/project_build_arm/dns323/.root
  make O=$BLDDIR

This way the toolchain, kernel, and already built packages are not
rebuilt, only the root directory is repopulated and the rootfs rebuild.

If in the next build you see that system libraries are being rebuild, *they will
be on error!*

Remaking a package
=================

To remake only a package, you should delete its directory under
$BLDDIR/build_arm, and
a) remove in $BLDDIR/project_build_arm/dns323/autotools-stamps/ the file with the package name, or
b) if none is found, remove from
 $BLDDIR/project_build_arm/dns323/root the package target file.
You can edit the package makefile in packages/<package-name>/<package-name>.mk

Hopping that there are no inaccuracies.

}}}