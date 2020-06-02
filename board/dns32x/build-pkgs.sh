#!/bin/bash

#set -x

build_fail() {
	if test -z "$FORCE_BUILD"; then
		echo "$1 build failed. Stopping..."
		exit 1
	fi
	echo "$1 build failed. Continuing..."
}

SKIP_FORWARD=n
VAR_CACHE=output/var.cache

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

	# force alternate buildroot package name if manually set
	if [ "${largs}" != "${args}" ]; then
		bb_pkg="$largs"
		pkg_force="-force"
	else
		bb_pkg="$lpkg"
		pkg_force=""
	fi

	# skip if package already built (allow resume after failure)
	if [ -e output/pkgs/${lpkg}_*.ipk ]; then
		echo "skipping $lpkg package..."
		SKIP_FORWARD=y
		continue
	fi

	# only baseline files if not fast-forwarding
	if [ "$SKIP_FORWARD" != "y" ]; then
		./board/dns32x/mkpkg.sh -set
	else
		# resume running baseline after this package
		SKIP_FORWARD=n
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

	make olddefconfig
	make $bb_pkg 2>&1 > output/pkg-build.log || build_fail "$lpkg"
	./board/dns32x/mkpkg.sh $pkg_force $lpkg || build_fail "$lpkg"
#done
done < board/dns32x/pkgs/pkg.lst

# add Packages index
./board/dns32x/mkpkg.sh -index output/pkgs

echo "Package build complete!"
exit 0
