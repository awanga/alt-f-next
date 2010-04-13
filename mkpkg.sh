#!/bin/bash

# To create a new package, you must first do:
# 	./mkpkg.sh -set
# that records the current files in the rootfs in file "rootfsfiles.lst"
# than, do:
# 	make O=... menu-config
# and add the package to buildroot, then do:
# 	make O=...
# to build the package and populate the rootfs, then do:
# 	./mkpkg.sh <pkg>
# where <pkg> is the lower case name of the buildroot package name.
# You must then edit and correct ipkfiles/<pkg>.control, add any
# <pkg>.{conffiles | preinst | postinst | prerm | postrm} files
# and recreate the package:
# 	./mkpkg.sh <package name>
# 	
# If package "a" depends on package "b", you must first create the package
# "b", with the above procedure, and then create the package "a" 
# 
# If the file contents of a package changes, do:
# 	rm ipkfiles/<pkg>.lst
# and recreate the package:
# 	./mkpkg.sh <package name>
# This assumes that the rootfs file list, rootfsfiles.lst, is still valid.
# 
# A end user package, to appear in the web pages,
# must have the following files:
# 1 /etc/init.d/S8?<pkgname> with a field "TYPE=user"
# 2 /etc/<pkgname>.conf
# 3 /sbin/rc<pkgname> as a link to /usr/sbin/rcscript
#   this is done at boot time, must also be created at
#   install time, use ipkg postinst script?
# 4 /usr/www/cgi-bin/<pkgname>.cgi
# 5 /usr/www/cgi-bin/<pkgname>_proc.cgi

#set -x

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

if test $# = 0; then
	echo -e "usage: mkpkg.sh <package> |\n -set (creates rootfs file list) |\n -setroot (creates rootfs base file list) |\n -cleanroot (remove all files not in rootfs base file list)\n"
	sed -n '3,35p' $0
	exit 1
fi

CDIR=$(pwd)
PATH=$CDIR/bin:$PATH
IPKGDIR=$CDIR/ipkgfiles

ROOTFSFILES=$CDIR/rootfsfiles-base.lst
TFILES=$CDIR/rootfsfiles.lst
PFILES=$CDIR/pkgfiles.lst

case "$1" in
	"-set")
		cd $BLDDIR/project_build_arm/dns323/root
		if test -f $TFILES; then
			mv $TFILES $TFILES-
		fi
		find . ! -type d > $TFILES
		chmod -w $TFILES
		exit 0
		;;
	
	"-setroot")
		if test -f $TFILES; then
			mv $ROOTFSFILES $ROOTFSFILES-
		fi
	
		cd $BLDDIR/project_build_arm/dns323/root
		find . > $ROOTFSFILES
		chmod -w $ROOTFSFILES
		exit 0
		;;

	"-cleanroot")
		cd $BLDDIR/project_build_arm/dns323
		rm -rf newroot
		(cd root && cpio --quiet -pdm ../newroot < $ROOTFSFILES)
		mv root oldroot
		mv newroot root
		exit 0
		;;
esac

pkg=$1
PKGMK=$(find $CDIR/package -name $pkg.mk)	
PKGDIR=$(dirname $PKGMK)
PKG=$(echo $pkg | tr [:lower:] [:upper:])
eval $(sed -n '/^'$PKG'_VERSION[ :=]/s/[ :]*//gp' $PKGDIR/$pkg.mk)
version=$(eval echo \$${PKG}_VERSION)
ARCH=arm

if ! test -e $TFILES; then
	echo "file $TFILES not found, exiting"
	exit 1
fi
		
if test -z "$PKGMK"; then
	echo "Package $pkg not found,exiting."
	exit 1
fi

if ! test -f $IPKGDIR/$pkg.control; then # first time build

	# create minimum control file. User must edit it
	# and do a new "./mkpkg <package>
	# the "Depends" entry is just a helper, it has to be checked
	# and corrected		
	awk -v ver=$version '
		/config BR2_PACKAGE/ {
			printf "Package: %s\nVersion: %s\n", tolower(substr($2,13)), ver
		}
		/(depends|select)/ && /BR2_PACKAGE/ {
			for (i=1; i<=NF; i++) {
				p = tolower(substr($i,13));
				if (p != "")
					printf "Depends: %s\n", p;
			}
		}
		/\thelp/,/^\w/ {
			a=substr($0,1,1);
			if (a != "" && a != "\t")
				exit;
			else
				if ($1 == "help")
					printf "Description: "
				else if ($1 != "")
					print $0
		}
		END {
			printf "Architecture: arm\n";
			printf "Priority: optional\n";
			printf "Section: admin\n";
			printf "Source: http://code.google.com/p/alt-f/\n";
			printf "Maintainer: jcard\n";
		}
	' $PKGDIR/Config.in > $IPKGDIR/$pkg.control
fi
	
if ! test -f $IPKGDIR/$pkg.lst; then # first time build
	# create file list
	cd ${BLDDIR}/project_build_arm/dns323/root	
	find . ! -type d > $PFILES
	
	diff $TFILES $PFILES | sed -n 's\> ./\./\p' > $IPKGDIR/$pkg.lst
	cd $CDIR
	rm $PFILES
fi

# in CONTROL:
# configuration files: conffiles (one line per configuration file)
# scripts to execute: preinst, postinst, prerm, and postrm
#	(variable PKG_ROOT defined as root of pkg installation)
#
# in $IPKGDI there will be:
# <pkg>.control, <pkg>.lst, <pkg>.conffiles, 
# <pkg>.preinst, <pkg>.postinst, <pkg>.prerm, <pkg>.postrm

mkdir -p tmp tmp/CONTROL

(cd ${BLDDIR}/project_build_arm/dns323/root && \
	cpio --quiet -pdmu $CDIR/tmp < $IPKGDIR/$pkg.lst)

for i in control conffiles preinst postinst prerm postrm; do
	if test -f $IPKGDIR/$pkg.$i; then
		cp $IPKGDIR/$pkg.$i tmp/CONTROL/$i
		if test ${i:0:1} = "p"; then
			chmod +x tmp/CONTROL/$i
		fi
	fi
done

ipkg-build -o root -g root tmp

mv ${pkg}_${version}_${ARCH}.ipk pkgs
rm -rf tmp

# my own "sm" ipkg-build
#tar -C ${BLDDIR}/project_build_arm/dns323/root -T $IPKGDIR/$pkg.lst -czf data.tar.gz
#tar -czf control.tar.gz ./control
#echo "2.0" > tmp/debian-binary
#ar -crf ${pkg}_${version}_arm.ipk ./debian-binary ./data.tar.gz ./control.tar.gz 
#rm data.tar.gz control control.tar.gz debian-binary
