#!/bin/bash

usage() {
	echo -e "\nusage: pkgs-check.sh -n(ew) | -s(same) | -u(pgraded) | -c(opy) | -h(elp)"
	echo -e "\tchecks packages in pkgs against sourceforge released package,
	showing identical, news and upgraded packages.
	with -c, copy new/upgraded packags to sourceforge"
	exit 1
}

copyf() {
	echo cp pkgs/${1}_arm.ipk sourceforge/pkgs/unstable
	cnt=$((cnt+1))
}

while getopts nsuch opt; do
	case $opt in
	n) new=y ;;  # new packages
	s) same=y ;; # identical 
	u) upg=y ;;  # upgraded
	c) copy=y;;  # copy
	*|h) usage ;;
	esac
done

for i in pkgs/*.ipk; do
	f=$(basename $i _arm.ipk)

	eval $(echo $f | awk -F_ '{printf("pkg=%s; ver=%s;", $1, $2)}')

	if test -n "$same" -a -f sourceforge/pkgs/unstable/${f}_arm.ipk; then
		echo $pkg: same
		continue
	fi

	if test -n "$new" && \
		! ls sourceforge/pkgs/unstable/${pkg}_*_arm.ipk > /dev/null 2>&1; then
		echo "$pkg: new"

		if test -n "$copy"; then copyf $f; fi
		continue
	fi

	if test -n "$upg" -a \
		! -f sourceforge/pkgs/unstable/${f}_arm.ipk && \
		ls sourceforge/pkgs/unstable/${pkg}_*_arm.ipk > /dev/null 2>&1; then

		echo -n "$pkg: $ver ("
		for j in $(ls sourceforge/pkgs/unstable/${pkg}_*_arm.ipk 2>/dev/null); do
			jf=$(basename $j _arm.ipk)
			eval $(echo $jf | awk -F_ '{printf("jpkg=%s; jver=%s;", $1, $2)}')
			echo -ne "$jver "
		done
		echo -e "\b)"

		if test -n "$copy"; then copyf $f; fi
	fi
done


if test -n "$copy" -a -n "$cnt"; then
	echo ./mkpkg -index sourceforge/pkgs/unstable/
fi
