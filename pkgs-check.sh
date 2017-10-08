#!/bin/bash

# find more than 2 pkgs:
# ls sourceforge/pkgs/unstable/ | cut -d_ -f1 | uniq -c | grep ^[[:space:]]*3

usage() {
	echo -e "\nusage: pkgs-check.sh -n(ew) | -s(same) | -u(pgraded) | -c(opy) | -d(not build) | -h(elp)"
	echo -e "\tchecks packages in pkgs against sourceforge released package,
	showing identical, news and upgraded packages.
	with -c, copy new/upgraded packags to sourceforge"
	exit 1
}

copyf() {
	cp pkgs/${1}_arm.ipk sourceforge/pkgs/unstable
	cnt=$((cnt+1))
}

if test $# = 0; then usage; fi

while getopts nsucdh opt; do
	case $opt in
	n) new=y ;;  # new packages
	s) same=y ;; # identical 
	u) upg=y ;;  # upgraded
	c) copy=y ;;  # copy
	d) notbuilt=y ;;
	*h) usage ;;
	esac
done

# not build packages present in ipkgfiles/*.control)
# usefull to see discontinued pkgs that still have control files
if test -n "$notbuilt"; then
	for i in ipkgfiles/*.control; do
		v=$(awk '/^Version/{print $2}' $i)
		f=$(basename $i .control)
		if ! test -f pkgs/${f}_${v}_arm.ipk; then
			echo "${f}_${v}"
		fi
	done
	exit 0
fi

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
	./mkpkg.sh -index sourceforge/pkgs/unstable/
fi
