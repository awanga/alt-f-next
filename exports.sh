if test $# = 0; then
	echo "error, supply absolute build dir as argument"
elif ! test -d $1; then
	echo "\"$1\" does not exists or is not a directory"
else
	export BLDDIR=$1
	export ROOTFS=$BLDDIR/project_build_arm/dns323/root
	export STAGING=$BLDDIR//build_arm/staging_dir
	export BINARIES=$BLDDIR/binaries/dns323
	export PATH=$HOME/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/opt/kde3/bin:~/Alt-F/alt-f/bin:$BLDDIR/build_arm/staging_dir/usr/bin
	export EDITOR=uemacs
fi
