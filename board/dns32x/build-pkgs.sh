#!/bin/bash

#set -x

build_fail() {
	if test -z "$FORCE_BUILD"; then
		echo "$1 build failed. Stopping..."
		exit 1
	fi
	echo "$1 build failed. Continuing..."
}

# scrub_file(file_path, pattern)
scrub_file() {
	sed -i "/.*${2}\$/d" $1
}

VAR_CACHE=output/var.cache

# baseline root filesystem before building pkgs (if not yet done)
if [ ! -f output/rootfsfiles-base.lst ]; then
	./board/dns32x/mkpkg.sh -setroot
fi

while IFS= read -r pkgargs; do

	# skip commented and blank lines
	if [[ "$pkgargs" =~ ^#.*+$ ]]; then continue; fi;
	if [[ "$pkgargs" =~ ^[\s]*+$ ]]; then continue; fi;

	# store any manual package arguments
	lpkg="${pkgargs%%:*}"
	args="${pkgargs##*:}"

	# separate manual buildroot package name and configuration flags
	largs="${args%%\;*}"
	args="${args##*\;}"

	pkg_clean=""

	# force alternate buildroot package name if manually set
	if [ "${largs}" != "${args}" ]; then

		# check for leading minus to allow pkg rebuild
		if [[ "$largs" =~ ^\-.*+$ ]]; then
			largs="${largs#?}"
			pkg_clean="y"
		fi

		bb_pkg="$largs"
		pkg_force="-force"
	else
		bb_pkg="$lpkg"
		pkg_force=""
	fi

	# skip if package already built (allow resume after failure)
	if [ -f output/pkgs/${lpkg}_*.ipk ]; then
		echo "skipping $lpkg package..."
		continue
	fi

	# remove any previous builds if indicated
	if [ "$pkg_clean" == "y" ]; then
		rm -fR ./output/build/$bb_pkg-*
	fi

	# find conditionals and append to the config file
	for arg in ${args//,/ }; do
		if [[ "$arg" = "$lpkg" ]]; then
			arg=${arg//-/_}
			echo "BR2_PACKAGE_${arg^^}=y" >> .config
		else
			if [[ "$arg" =~ ^#.*+$ ]]; then
				echo "# ${arg//#/} is not set"
			else
				echo "$arg" >> .config
			fi
		fi
	done

	./board/dns32x/mkpkg.sh -set
	make olddefconfig
	make $bb_pkg 2>&1 > output/pkg-build.log || build_fail "$lpkg"

	# overwrite pkg list when environment variable is set
	if [ "$OVERWRITE_PKG_LST" != "" ]; then
		PKG_DIFF=$(mktemp)
		./board/dns32x/mkpkg.sh -diff > $PKG_DIFF
		# catch null case and avoid zeroing out pkg file list
		if [[ $(cat $PKG_DIFF) != "" ]]; then
			scrub_file $PKG_DIFF ".a"
			scrub_file $PKG_DIFF ".la"
			scrub_file $PKG_DIFF "\/etc\/rc[0-9].d.*"
			scrub_file $PKG_DIFF "\/usr\/include.*"
			scrub_file $PKG_DIFF "\/usr\/doc.*"
			scrub_file $PKG_DIFF "\/usr\/lib\/cmake.*"
			scrub_file $PKG_DIFF "\/usr\/lib\/pkgconfig.*"
			scrub_file $PKG_DIFF "\/usr\/man.*"
			scrub_file $PKG_DIFF "\/usr\/share\/aclocal.*"
			scrub_file $PKG_DIFF "\/usr\/share\/bash-completion.*"
			scrub_file $PKG_DIFF "\/usr\/share\/doc.*"
			scrub_file $PKG_DIFF "\/usr\/share\/info.*"
			scrub_file $PKG_DIFF "\/usr\/share\/locale.*"
			scrub_file $PKG_DIFF "\/usr\/share\/.*\-doc.*"
			scrub_file $PKG_DIFF "\/usr\/share\/man.*"
			scrub_file $PKG_DIFF "\/var\/.*"
			cat $PKG_DIFF > board/dns32x/ipkgfiles/$lpkg.lst
		fi
		rm $PKG_DIFF
	fi

	fakeroot ./board/dns32x/mkpkg.sh $pkg_force $lpkg || build_fail "$lpkg"

done < board/dns32x/pkgs/pkg.lst

# add Packages index
./board/dns32x/mkpkg.sh -index output/pkgs

echo "Package build complete!"
exit 0
