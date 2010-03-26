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

cp $BLDDIR/binaries/dns323/zImage \
	$BLDDIR/binaries/dns323/rootfs.arm.cpio-sq.lzma \
	reloaded/alt-f

# don't compress, no significant space saving and much slower extraction
(cd reloaded; tar cvf alt-f.tar alt-f)
