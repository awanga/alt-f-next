#!/bin/sh

# update all package developer version in package control file after a uclibc change
# package aaa-1.2.3-1 is increased to aaa-1.2.3-2 and bbb-1.2.3 is increased to bbb-1.2.3-1

# it start verifying for each package control file the existence of a released package
# only released packages are updated.
# then it extracts the version and developper version from the control file, 
# increases it and updates the control file

read -p "This will bump version of all ipkg control files. Are you sure? (yes/no)" ans

if test "$ans" != "yes"; then exit ; fi

for i in ipkgfiles/*.control; do
	f=$(basename $i .control)

	# package name
	p=$(sed -n '/Package/s/Package: \(.*\)/\1/p' $i)

	# old version released
	ov=$(sed -n '/Version/s/Version: \(.*\)/\1/p' $i)

	if ! test -f sourceforge/pkgs/unstable/${p}_${ov}_arm.ipk; then
		if ! test -f pkgs/${p}_${ov}_arm.ipk; then
			echo "------> Missing: $p-$ov"
		fi
		continue
	fi

	# version
	v=$(sed -n '/Version/s/Version: \(.*\)-.$/\1/p' $i)
	if test -z "$v"; then
		v=$(sed -n '/Version/s/Version: \(.*\)/\1/p' $i)
	fi

	# new release
	r=$(sed -n '/Version/s/.*-\(.\)$/\1/p' $i)
	if test -z "$r"; then
		r="1"
	else
		r=$((r+1))
	fi

	echo -e "updating package $f from $ov to $v-$r"

	# the editing
	sed -i '/Version:/s/Version:.*/Version: '$v-$r'/' $i

done
