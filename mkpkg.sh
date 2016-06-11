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
set -u

usage() {
	echo -e "usage: mkpkg.sh <package> |
	-rm <package> (remove from rootfs files from <pkg> |
	-ls <package> (list package file contents) |
	-check [package] (verify package|all files existence)
	-set (store current rootfs file list) |
	-clean (remove new files since last -set) |
	-diff (show new files since last -set) |
	-force <package> (force create package. You must first create the .control file) |
	-setroot (creates rootfs base file list) |
	-cleanroot (remove all files not in rootfs base file list) |
	-diffroot (show new files since last -setroot) |
	-debris (shows files not owned by any package) |
	-miss (shows base firmware missing files) |
	-index <pkg_dir> (create ipkg package index) |
	-html (output packages info in html format)
	-all (recreates all packages in ipkfiles dir) |
	-rmall (remove from rootfs files from all packages) |
	-help"
	exit 0
}

if test "$(dirname $0)" != "."; then
	echo "This script must be run in the root of the tree."
	exit 1;
fi

if test -z "$BLDDIR"; then
	echo "Run '. exports [board]' first."
	exit 1
fi

if test $# = 0; then
	usage
fi

mkdir -p pkgs

CDIR=$(pwd)
PATH=$CDIR/bin:$PATH
IPKGDIR=$CDIR/ipkgfiles

. .config 2> /dev/null
BOARD=$BR2_PROJECT

ROOTFSDIR=$BLDDIR/project_build_arm/$BOARD/root

ROOTFSFILES=$CDIR/rootfsfiles-base.lst
TFILES=$CDIR/rootfsfiles.lst
PFILES=$CDIR/pkgfiles.lst

force=n

case "$1" in
	-rm)
		if test $# != 2 -o ! -f $IPKGDIR/$2.lst; then
			usage
		fi
		#if ! grep -q ^BR2_PACKAGE_$(echo $2 | tr '[:lower:]-' '[:upper:]_') .config; then
		#	echo package $2 not configured
		#	exit 1
		#fi
		rm -f $BLDDIR/project_build_arm/$BOARD/autotools-stamps/$2_*
		cd $ROOTFSDIR
		# remove files first
		xargs --arg-file=$IPKGDIR/$2.lst rm -f >& /dev/null
		# and then empty directories. reverse sort to remove subdirs first
		cat $IPKGDIR/$2.lst | sort -r | xargs rmdir >& /dev/null
		exit 0
		;;

	-ls)
		if test $# != 2 -o ! -f $IPKGDIR/$2.lst; then
			usage
		fi
		cd $ROOTFSDIR
		xargs --arg-file=$IPKGDIR/$2.lst ls
		exit $?
		;;

	-set)
		cd $ROOTFSDIR
		if test -f $TFILES; then
			mv $TFILES $TFILES-
		fi
		#find . ! -type d | sort > $TFILES
		find . | sort > $TFILES
		chmod -w $TFILES
		exit 0
		;;

	-diff)
		cd $ROOTFSDIR
		TF=$(mktemp)
		#find . ! -type d | sort > $TF
		find . | sort > $TF
		diff $TFILES $TF | sed -n 's\> ./\./\p'
		rm $TF
		exit 0
		;;

	-clean)
		#tf=$(mktemp -t)
		cd $ROOTFSDIR
		find . | cat $TFILES - | sort | uniq -u | xargs rm >& /dev/null # $tf
		#awk '/Is a directory/{print substr($4,2,length($4)-3)}' $tf | sort -r | xargs rmdir
		find . | cat $TFILES - | sort -r | uniq -u | xargs rmdir >& /dev/null
		#rm $tf
		exit 0
		;;

	-force)
		if test "$#" != 2; then usage; fi
		shift
		force=y
		;;

	-setroot)
		# records the current files in the rootfs
		# must be done after the first make with only the base packages configured
		if test -f $ROOTFSFILES; then
			mv $ROOTFSFILES $ROOTFSFILES-
		fi
	
		cd $ROOTFSDIR
		#find . ! -type d | sort > $ROOTFSFILES
		find . | sort > $ROOTFSFILES
		chmod -w $ROOTFSFILES
		exit 0
		;;

	-cleanroot)
		# remove all files found in the rootfs after the last "-setroot"
		# to recreate the rootfs.ext2, a make with the base system configured must be done
		#tf=$(mktemp -t)
		cd $ROOTFSDIR
		find . | cat $ROOTFSFILES - | sort | uniq -u | xargs rm >& /dev/null # $tf
		#awk '/Is a directory/{print substr($4,2,length($4)-3)}' $tf | sort -r  | xargs rmdir
		find . | cat $ROOTFSFILES - | sort -r | uniq -u | xargs rmdir >& /dev/null
		#rm $tf
		exit 0
		;;

	-diffroot)
		cd $ROOTFSDIR
		TF=$(mktemp)
		#find . ! -type d | sort > $TF
		find . | sort > $TF
		diff $ROOTFSFILES $TF | sed -n 's\> ./\./\p'
		rm $TF
		exit 0
		;;

	-index)
		if test "$#" != 2; then usage; fi
		shift
		ipkg-make-index $1 > $1/Packages
		exit 0
		;;

	-all)
		gst=0; skp=0;
		for i in $(ls $IPKGDIR/*.control); do
			p=$(basename $i .control)
			if grep -q ^BR2_PACKAGE_$(echo $p | tr '[:lower:]-' '[:upper:]_')=y .config; then
				echo -n Creating package ${p}...
				res=$(./mkpkg.sh $p)
				st=$?
				if test -n "$res"; then res="($res)"; fi
				if test $st = 0; then
					echo -e "\tOK $res" 
				else
					echo -e "\tFAIL $res"
				fi
				gst=$((gst+st))
			else
				echo -e "Creating package ${p}...\tskipping (not configured)."
				((skp++))
			fi
		done
		echo "$skp package(s) skipped."
		if test $gst != 0; then
			echo "$gst package(s) FAILED."
		else
			echo "All packages build OK."
		fi
		ipkg-make-index pkgs/ > pkgs/Packages
		exit $gst
		;;

	-check)
		if test "$#" = 2; then
			./mkpkg.sh -ls $2 1> /dev/null
			exit $?
		else
			for i in $(ls $IPKGDIR/*.control); do
				p=$(basename $i .control)
				if grep -q ^BR2_PACKAGE_$(echo $p | tr '[:lower:]-' '[:upper:]_')=y .config; then
					if ! ./mkpkg.sh -ls $p >& /dev/null; then
						echo "Package $p FAILS"
					else
						echo "Package $p OK"
					fi
				fi
			done
		fi
		exit 0
		;;

	-debris)
		# create list of currently configured packages files.
		# some package file list don't include directories, so debris dirs  are not displayed
		TF=$(mktemp)
		for i in $(ls $IPKGDIR/*.lst); do
			p=$(basename $i .lst)
			if grep -q ^BR2_PACKAGE_$(echo $p | tr '[:lower:]-' '[:upper:]_')=y .config; then
				cat $i >> $TF 
			fi
		done

		# remove base files and package files from current rootfs lst. Left files are debris
		TF1=$(mktemp); TF2=$(mktemp)
		(cd $ROOTFSDIR; find . > $TF1)
		for i in $(sort $TF $TF1 $ROOTFSFILES | uniq -u); do
			if test -f $ROOTFS/$i; then
				echo $i
			fi
		done
		#echo $TF $TF1 $TF2
		rm $TF $TF1 $TF2
		exit 0
		;;

	-miss)
		for i in $(cat $ROOTFSFILES); do
			if ! test -f $ROOTFS/$i -o -d $ROOTFS/$i; then
				echo $i
			fi
		done
		exit 0
		;;

	-rmall)
		for i in $(ls $IPKGDIR/*.control); do
			p=$(basename $i .control)
			echo -n Removing files from package ${p}...
			res=$(./mkpkg.sh -rm $p)
			if test $? != 0; then
				echo " FAIL ($res)"
			else
				echo " OK"
			fi
		done
		exit 0
		;;

	-html)
		cat<<-EOF
			<table><tr><th>Package</th><th>Version</th><th>Description</th></tr>
			<tr><td colspan=3><br><strong>uPNP A/V servers</strong></td></tr>
			<tr><td colspan=3><br><strong>BitTorrent</strong></td></tr>
			<tr><td colspan=3><br><strong>Printing/scanning</strong></td></tr>
			<tr><td colspan=3><br><strong>Misc Tools</strong></td></tr>
			<tr><td colspan=3><br><strong>Development/ CLI utilities</strong></td></tr>
			<tr><td colspan=3><br><strong>Networking</strong></td></tr>
			<tr><td colspan=3><br><strong>Databases</strong></td></tr>
			<tr><td colspan=3><br><strong>Transcoding</strong></td></tr>
			<tr><td colspan=3><br><strong>Libraries</strong></td></tr>

		EOF
		for i in  ipkgfiles/*.control ; do
			awk '/Package:/ {pkg=$2} 
				/Description:/ {desc=substr($0,index($0,":")+1)} 
				/Version:/ {ver=$2} 
				END {printf "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n", pkg, ver, desc}' $i
		done
		echo "</table>"	
		exit 0
		;;

	-help|--help|-h)
		usage
		sed -n '3,35p' $0
		exit 1
		;;

	-*)
		usage
		;;
esac

ARCH=arm

pkg=$1
PKG=$(echo $pkg | tr '[:lower:]-' '[:upper:]_')

if test "$force" != "y"; then
	if test "$pkg" = "gdb" -a -n "$(grep '^BR2_PACKAGE_GDB=y' .config)"; then # special gdb case
		PKGDIR=toolchain/gdb
		version=$(sed -n 's/^BR2_GDB_VERSION="\(.*\)"/\1/p' .config)
	else
		PKGMK=$(find $CDIR/package -name $pkg.mk)
		if test -z "$PKGMK"; then
			#echo Package $pkg not found, is it a sub-package?
			
			if grep -q "^BR2_PACKAGE_$PKG=y" .config; then
				MPKGMK=$(echo $pkg | awk -v CDIR=$CDIR -F - '{
					res = $1
					for (i=2; i<=NF+1; i++) {
						cmd="find "CDIR"/package -name " res ".mk"
						if (cmd | getline var) {
							print var; exit;
						} else {
							res=res "-" $i
						}
					}
				}')

				if test -z "$MPKGMK"; then
					echo main package of $pkg not found.
					exit 1
				fi

				mpkg=$(basename $MPKGMK .mk)
				MPKG=$(echo $mpkg | tr '[:lower:]-' '[:upper:]_'  )

			else
				echo $pkg is not configured.
				exit 1
			fi

			echo $pkg is a sub-package of $mpkg
			PKGDIR=$(dirname $MPKGMK)
			if true; then
				# faster, but does not expand makefile variables nor takes conditionals into account
				eval $(sed -n '/^'$MPKG'_VERSION[ :=]/s/[ :]*//gp' $PKGDIR/$mpkg.mk)
				version=$(eval echo \$${MPKG}_VERSION)
			else
				version=$(make O=$BLDDIR -p -n $mpkg 2>/dev/null | sed -n '/^'$MPKG'_VERSION[ :=]/s/.*=[ ]\(.*\)/\1/p')
			fi
		elif grep -q "^BR2_PACKAGE_$PKG=y" .config; then
			PKGDIR=$(dirname $PKGMK)
			if true; then
				# faster, but doesn't expand makefile variables nor takes conditionals into account
				eval $(sed -n '/^'$PKG'_VERSION[ :=]/s/[ :]*//gp' $PKGDIR/$pkg.mk)
				version=$(eval echo \$${PKG}_VERSION)
			else
				version=$(make O=$BLDDIR -p -n $pkg 2>/dev/null | sed -n '/^'$PKG'_VERSION[ :=]/s/.*=[ ]\(.*\)/\1/p')
			fi
		else
			echo $pkg is not configured.
			exit 1
		fi
	fi
fi

#echo pkg=$pkg PKG=$PKG mpkg=$mpkg MPKG=$MPKG version=$version

if ! test -f $IPKGDIR/$pkg.control; then # first time build

	# create minimum control file. User must edit it
	# and do a new "./mkpkg <package>
	# the "Depends" entry is just a helper, it has to be checked
	# and corrected

	awk -v ver=$version -v pkg=$pkg '
		BEGIN { deps = "ipkg" }
		/(depends|select)/ && /BR2_PACKAGE/ {
			for (i=1; i<=NF; i++) {
				p = tolower(substr($i,13));
				if (p != "")
					deps = p ", " deps ;
			}
		}
		/\thelp/,/^\w/ {
			a=substr($0,1,1);
			if (a != "" && a != "\t")
				exit;
			else if ($1 != "" && $1 != "help")
				desc = desc $0 "\n";
		}
		END {
			printf "Package: %s\n", pkg;
			printf "Description: %s", desc;
			printf "Version: %s\n", ver;
			if (deps != "")
				printf "Depends: %s\n", deps;
			printf "Architecture: arm\n";
			printf "Priority: optional\n";
			printf "Section: admin\n";
			printf "Source: http://code.google.com/p/alt-f/\n";
			printf "Maintainer: jcard\n";
		}
	' $PKGDIR/Config.in > $IPKGDIR/$pkg.control
elif test "$force" != "y"; then 
	cver=$(awk '/^Version/{print $2}' $IPKGDIR/$pkg.control)
 	if test "$cver" != "$version"; then
		if test "${cver%-[0-9]}" != "$version"; then
			echo $pkg.control has version $cver and built package has version $version.
			exit 1
		else
			version=$cver
		fi
	fi
else
	version=$(awk '/^Version/{print $2}' $IPKGDIR/$pkg.control)
fi

if ! test -f $IPKGDIR/$pkg.lst; then # first time build
	if ! test -e $TFILES; then
		echo "file $TFILES not found, read help."
		exit 1
	fi

	# create file list
	cd $ROOTFSDIR	
	find . | sort > $PFILES

	diff $TFILES $PFILES | sed -n 's\> ./\./\p' > $IPKGDIR/$pkg.lst
	cd $CDIR
	rm $PFILES
fi

# in CONTROL:
# configuration files: conffiles (one line per configuration file)
# scripts to execute: preinst, postinst, prerm, and postrm
#	(variable PKG_ROOT defined as root of pkg installation)
#
# in $IPKGDIR there will be:
# <pkg>.control, <pkg>.lst, <pkg>.conffiles, 
# <pkg>.preinst, <pkg>.postinst, <pkg>.prerm, <pkg>.postrm

mkdir -p tmp tmp/CONTROL

cd ${BLDDIR}/project_build_arm/$BOARD
#cd root
#cpio --quiet -pdu $CDIR/tmp < $IPKGDIR/$pkg.lst
# cpio creates needed directories ignoring umask, so use tar
# but using tar with a pipe, if the first tar fails we can't know it,
# so check files first
grep -v '^#' $IPKGDIR/$pkg.lst > $IPKGDIR/$pkg.lst-noc
for i in $(cat $IPKGDIR/$pkg.lst-noc); do
	if test ! -e root/$i -a ! -h root/$i; then
		echo "failed creating $pkg package ($i not found)"
		exit 1
	fi
done

tar -C root -c --no-recursion -T $IPKGDIR/$pkg.lst-noc | tar -C $CDIR/tmp -x
if test $? = 1; then 
	echo failed creating $pkg package
	exit 1
fi
cd "$CDIR"

rm -f $IPKGDIR/$pkg.lst-noc

for i in control conffiles preinst postinst prerm postrm; do
	if test -f $IPKGDIR/$pkg.$i; then
		cp $IPKGDIR/$pkg.$i tmp/CONTROL/$i
		if test ${i:0:1} = "p"; then
			chmod +x tmp/CONTROL/$i
		fi
	fi
done

ipkg-build -o root -g root tmp

pname=$(awk '/^Package:/{print $2}' $IPKGDIR/$pkg.control) # underscores in pkg name
mv ${pname}_${version}_${ARCH}.ipk pkgs
rm -rf tmp

# my own "sm" ipkg-build
#tar -C ${BLDDIR}/project_build_arm/dns323/root -T $IPKGDIR/$pkg.lst -czf data.tar.gz
#tar -czf control.tar.gz ./control
#echo "2.0" > tmp/debian-binary
#ar -crf ${pkg}_${version}_arm.ipk ./debian-binary ./data.tar.gz ./control.tar.gz 
#rm data.tar.gz control control.tar.gz debian-binary
