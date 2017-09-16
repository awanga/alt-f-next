#!/bin/sh

#set -x

if test "$(dirname $0)" != "."; then
        echo "This script must be run in the root of the tree, exiting."
        exit 1;
fi

if test $# = 1; then
	kver=$1
else
	if test -f .config; then
		. ./.config 2> /dev/null
	else
		echo "Not configured, run '. exports [board]' first."
		exit 1
	fi

	kver=$BR2_CUSTOM_LINUX26_VERSION
fi

aufssite=git://aufs.git.sourceforge.net/gitroot/aufs

case $kver in
	3.10.32) aufsver=3.10.x ;;
	3.18.28|3.18.37) aufsver=3.18.25+ ;;
	4.4.45|4.4.86) aufsver=4.4; aufssite=git://github.com/sfjro ;;
	*) echo "No aufs configuration found for kernel $kver, exiting."
		exit 1;;
esac

aufsnm=aufs${aufsver:0:1}

kh=$(pwd)/toolchain/kernel-headers/linux-$kver

if ! test -d ${aufsnm}-standalone.git; then
	git clone \
	${aufssite}/${aufsnm}-standalone.git ${aufsnm}-standalone.git
fi

cd ${aufsnm}-standalone.git

rm -rf a b

git remote update
git checkout origin/aufs${aufsver}

#git branch
#git pull
#git status

cp ${aufsnm}-kbuild.patch $kh-00-${aufsnm}-kbuild.patch
cp ${aufsnm}-base.patch $kh-01-${aufsnm}-base.patch
cp ${aufsnm}-mmap.patch $kh-02-${aufsnm}-mmap.patch

mkdir a b

cp -a {Documentation,fs,include} b
rm b/include/uapi/linux/Kbuild
#cp b/include/uapi/linux/aufs_type.h b/include/linux/
diff -rupN a/ b/ > $kh-03-${aufsnm}.patch

echo "Generated aufs patches $aufsver for kernel $kver"

cd ..
