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

ver=$(cut -f2 -d" " customroot/etc/Alt-F)

cd reloaded

if ! test -f alt-f/reloaded-2.6.12.6-arm1.ko; then
	if ! test -f ffp-reloaded-0.5-2.tgz; then
		wget http://www.inreto.de/dns323/ffp-reloaded/packages/ffp-reloaded-0.5-2.tgz
	fi
	tar --wildcards -xzf ffp-reloaded-0.5-2.tgz ./ffp/boot/reloaded-\*
	mv ffp/boot/reloaded-* alt-f
	rm -rf ffp
fi

cp $BLDDIR/binaries/dns323/zImage \
	$BLDDIR/binaries/dns323/rootfs.arm.cpio-sq.lzma \
	alt-f

# don't compress, no significant space saving and much slower extraction
rm alt-f/*~ >& /dev/null
tar --exclude-vcs -cvf Alt-F-$ver.tar alt-f
mv Alt-F-$ver.tar $BLDDIR/binaries/dns323/
