#!/bin/bash

#The ideia is to add a new package, make, and compare the new filesystem
#files with the initial filesystem files, create a list of differences,
#create the archive, and finally remove the files from the filesystem.
#
#This approch has problems for pakages the depends on others; one must first
#create the dependencies packages and archives, one by one, and finally the
#final package.
#This only works for autotools configured packages, as we can remove the files
#from the filesystem -- as the final package is configured against the stagging
#dir, and the dependencies are there, they are not installed again (as long as
#their stamps does not disappear from the 
#project_build_arm/dns323-pkg/autotools-stamps dir

# A package must have the following files:
# 1 /etc/init.d/S8?<pkgname> with a field "TYPE=user"
# 2 /etc/<pkgname>.conf
# 3 /sbin/rc<pkgname> as a link to /usr/sbin/rcscript
# 4 /usr/www/cgi-bin/<pkgname>.cgi
# 5 /usr/www/cgi-bin/<pkgname>_proc.cgi

#set -x

CDIR=~jcard/Desktop/buildroot-2009.08
BRDIR=~jcard/Desktop/buildroot-2009.08-build-2
RFILES=rootfsfiles.lst
PFILES=pkgfiles.lst

if test $# = 0; then
	echo "usage: mkpkg.sh <package> | -set (creates default file list)
		-run 'mkpkg.sh <pkg>' after adding a new package;
		 it will create a <pkg>.pkg  archive which contains <pkg>.ctr
		 and <pkg>.tgz with the new files in the rootfs
		 (and remove them from the fs?)
		-run 'mkpkg.sh -set' to record the files of a full rootfs
		 without any extra packages."
		
	exit 1
fi

if test "$1" = "-set"; then

	cd ${BRDIR}/project_build_arm/dns323
	if test -e $RFILES; then
		mv $RFILES $RFILES-safe
	fi

	(cd root && find . ! -type d ) > $RFILES
	chmod -w $RFILES

	exit 0
fi

echo TODO: add revision= and conf= to ctr file

pkg=$1
PKGMK=$(find $CDIR/package -name $pkg.mk)

if test -z "$PKGMK"; then
	echo package $pkg not found
	exit 1
fi

PKGDIR=$(dirname $PKGMK)
PKG=$(echo $pkg | tr [:lower:] [:upper:])

eval $(sed -n '/^'$PKG'_VERSION[ :=]/s/[ :]//gp' $PKGDIR/$pkg.mk)
version=$(eval echo \$${PKG}_VERSION)

name=$pkg-$version

cd ${BRDIR}/project_build_arm/dns323

awk -v v=$version '
	/config BR2_PACKAGE/ {
	printf "package=%s\nversion=%s\n", tolower(substr($2,13)), v
	}
	/(depends|select)/ && /BR2_PACKAGE/ {
	for (i=1; i<=NF; i++) {
		p = tolower(substr($i,13));
		if (p != "")
			printf "depends=%s\n", p;
	}
	}
	END {
	printf "files=\"";
}' $PKGDIR/Config.in > $pkg.ctr

if ! test -e $RFILES; then
	echo "file $PWD/$RFILES not found, exiting"
	exit 1
fi

(cd root && find . ! -type d ) > $PFILES

diff $RFILES $PFILES | sed -n 's\> ./\\p' > $pkg.lst
cat $pkg.lst >> $pkg.ctr
echo "\"" >> $pkg.ctr

tar -C root -T $pkg.lst -cvzf $pkg.tgz
ar -cr $name.pkg $pkg.ctr $pkg.tgz

rm $PFILES $pkg.tgz $pkg.ctr $pkg.lst

exit 

read -p "Continue <enter>"? cont
if test -n "$cont"; then echo "Abort"; exit 1; fi

# uncomment? next, debugging
#(cd root && cat ../${name}.lst | xargs rm) # remove files from rootfs?
#mv ${name}.tgz ${name}.lst $BRDIR/binaries/dns323-pkg
