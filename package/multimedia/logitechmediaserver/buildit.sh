#!/usr/bin/env bash

# a cleaner alternative to 'buildme.sh' for cross compiling under linux/Alt-F
# needs as environment variables CROSS, CC, ICU_HOST_DIR, PERL_SRC,and optionaly CFLAGS, CXXFLAGS

# didn't Logitech ever heard of makefiles?!!! SHAME!!!

OS=`uname`

# get system arch, stripping out extra -gnu on Linux
ARCH=`/usr/bin/perl -MConfig -le 'print $Config{archname}' | sed 's/gnu-//' | sed 's/^i[3456]86-/i386-/' | sed 's/armv5tejl/arm/' `

if [ $OS != "Linux" ]; then
    echo "Unsupported platform: $OS, please submit a patch or provide us with access to a development system."
    exit
fi

if [ ! -x /usr/bin/rsync ]; then
    echo "This script requires /usr/bin/rsync, please install it."
    exit
fi

# Build dir
BUILD=$PWD/build

# try to use default perl version
if [ "$PERL_BIN" = "" ]; then
    PERL_BIN=`which perl`
    PERL_VERSION=`perl -MConfig -le '$Config{version} =~ /(\d+.\d+)\./; print $1'`
    
    case "$PERL_VERSION" in
    "5.16")
        PERL_516=$PERL_BIN
        ;;
    "5.18")
        PERL_518=$PERL_BIN
        ;;
    "5.20")
        PERL_520=$PERL_BIN
        ;;
    *)
        echo "Failed to find supported Perl version for '$PERL_BIN'"
        exit
        ;;
    esac

    echo "Building with Perl $PERL_VERSION at $PERL_BIN"
    PERL_BASE=$BUILD/$PERL_VERSION
    PERL_ARCH=$BUILD/arch/$PERL_VERSION
fi

if test -z "$CROSS"; then
	echo "Tou have to define CROSS and other variables, exiting"
	exit 1
fi

FLAGS="-fPIC"

CROSS_OPTS="--prefix=$BUILD --disable-dependency-tracking --enable-static \
	--with-pic --target=$CROSS --host=$CROSS"
eval $($PERL_BIN -V:ccflags | sed 's/-fstack-protector//')
eval $($PERL_BIN -V:cppflags | sed 's/-fstack-protector//')

CPPFLAGS="$cppflags"
LD_RUN_PATH=""
ARCH=$CROSS

CCFLAGS="$ccflags $FLAGS"
CFLAGS="$CFLAGS $FLAGS"
CXXFLAGS="$CXXFLAGS $FLAGS"
LDFLAGS="$LDFLAGS $FLAGS"
LDDLFLAGS="-shared $FLAGS"

# Clean up

rm -rf $BUILD/arch
mkdir -p $BUILD

# $1 = module to build
# $2 patch file
# $3 = Makefile.PL arg(s)
# $4 Makefile.PL subdir
function build_module {
	tg=${1%-*}
	if test -f .stamp-pm-$tg; then return; fi
	if ! test -f $1.tar.gz; then merror $tg; fi
	if test -n "$4"; then PLSUB=$4; else PLSUB=""; fi
	if test "$3" != "-"; then PLOPT="$3"; fi
	LPWD=$PWD
	td=$1

	echo ">>> Building perl module $td..."

	if ! test -d $td; then
		if ! tar xzf $td.tar.gz; then merror $tg; fi
		if test -f "$2"; then patch -p0 < $2; fi
	fi

	cd $td/$PLSUB
 
	export PERL5LIB=$PERL_BASE/lib/perl5
	$PERL_BIN Makefile.PL INSTALL_BASE=$PERL_BASE CC="$CC" CCFLAGS="$CCFLAGS" LD="$CC" LDFLAGS="$LDFLAGS" LDDLFLAGS="$LDDLFLAGS" PERL_SRC="$PERL_SRC" $PLOPT

	if ! make V=1 CC="$CC" CFLAGS="$CFLAGS" CCFLAGS="$CCFLAGS" CPPFLAGS="$CPPFLAGS" CXX="$CXX" CXXFLAGS="$CXXFLAGS" LD="$CC" LDFLAGS="$LDFLAGS" LDDLFLAGS="$LDDLFLAGS" LD_RUN_PATH="$LD_RUN_PATH"; then merror $tg; fi

	if ! make CC="$CC" CFLAGS="$CFLAGS" CCFLAGS="$CCFLAGS" CPPFLAGS="$CPPFLAGS" CXX="$CXX" CXXFLAGS="$CXXFLAGS" LD="$CC" LDFLAGS="$LDFLAGS" LDDLFLAGS="$LDDLFLAGS" LD_RUN_PATH="$LD_RUN_PATH"  install; then merror $tg; fi

    cd $LPWD
	touch .stamp-pm-$tg
}

#this is a hack!!!
# $1 = module to build
# $2 = Makefile.PL arg(s)
function build_host_module {
	tg=${1%-*}-host
	if test -f .stamp-pm-$tg; then return; fi

	td=$1-host
	echo ">>> Building perl host module $td..."

 	if ! test -d $td; then
		tar xzf $1.tar.gz
		mv $1 $td
		cd $td
		if test -f "../$2"; then patch -p1 < ../$2; fi
	else
		cd $td
		#if ! make clean; then merror $tg; fi
	fi

	export PERL5LIB=$PERL_BASE/lib/perl5
	$PERL_BIN Makefile.PL INSTALL_BASE=$PERL_BASE $2

	if ! make; then merror $tg; fi
	if ! make install; then merror $tg; fi

    cd ..
	touch .stamp-pm-$tg
}

function build_all {
    build Audio::Scan
    build Class::C3::XS
    build Class::XSAccessor
    build Compress::Raw::Zlib
    #build DBD::mysql
	build_host_module DBI-1.616 # build host DBI, DBD::SQLite needs it
    build DBD::SQLite
	build DBI # build target DBI, overrwritng the host installed one
    build Digest::SHA1
    build EV
    build Encode::Detect
    build HTML::Parser
    build Image::Scale
    build IO::AIO
    build IO::Interface
    build JSON::XS
    build Linux::Inotify2
    build Mac::FSEvents
    build Media::Scan
    build MP3::Cut::Gapless
    build Sub::Name
    build Template
    build XML::Parser
    build YAML::LibYAML
#    build Font::FreeType
#    build Locale::Hebrew
}

function build {
    case "$1" in
		Class::C3::XS)
			;;
        
        Class::XSAccessor)
			if [ "$PERL_516" -o "$PERL_518" -o "$PERL_520" ]; then
				build_module Class-XSAccessor-1.18
			else
				build_module Class-XSAccessor-1.05
			fi
			;;
        
        Compress::Raw::Zlib)
			;;
        
        DBI)
			if [ "$PERL_518" -o "$PERL_520" ]; then
				build_module DBI-1.628
			else
				build_module DBI-1.616
			fi
			;;
        
		DBD::SQLite)
			build_icu
			build_module DBD-SQLite-1.34_01 DBD-SQLite-1.34_01.patch
			;;
        
        Digest::SHA1)
			build_module Digest-SHA1-2.13
			;;
        
        EV)
			build_module common-sense-2.0
			PERL_MM_USE_DEFAULT=1 build_module EV-4.03 EV-4.03.patch
            ;;
        
        Encode::Detect)
			build_module Data-Dump-1.19
			build_module ExtUtils-CBuilder-0.260301
			build_module Module-Build-0.35
			build_module Encode-Detect-1.00
            ;;
        
        HTML::Parser)
			build_module HTML-Tagset-3.20
			build_module HTML-Parser-3.68
            ;;

        Image::Scale)
			build_libjpeg
			build_libpng
			build_giflib
			
			build_module Test-NoWarnings-1.02
			build_module Image-Scale-0.08 - "--with-jpeg-includes="$BUILD/include" --with-jpeg-static \
					--with-png-includes="$BUILD/include" --with-png-static \
					--with-gif-includes="$BUILD/include" --with-gif-static"            
            ;;
        
        IO::AIO)
			build_module common-sense-2.0
			build_module IO-AIO-3.71
            ;;
        
        IO::Interface)
            build_module IO-Interface-1.06
            ;;
        
        JSON::XS)
            build_module common-sense-2.0
            
            if [ "$PERL_518" -o "$PERL_520" ]; then
                build_module JSON-XS-2.34
            else
                build_module JSON-XS-2.3
            fi
            ;;
        
        Linux::Inotify2)
			build_module common-sense-2.0
			build_module Linux-Inotify2-1.21
            ;;
        
        Locale::Hebrew)
            build_module Locale-Hebrew-1.04
            ;;

        Mac::FSEvents)
            ;;
        
        Sub::Name)
            build_module Sub-Name-0.05
            ;;
        
        YAML::LibYAML)
            build_module YAML-LibYAML-0.35
            ;;
        
        Audio::Scan)
            build_module Sub-Uplevel-0.22
            build_module Tree-DAG_Node-1.06
            build_module Test-Warn-0.23
            build_module Audio-Scan-0.93
            ;;

        MP3::Cut::Gapless)
            build_module Audio-Cuefile-Parser-0.02
            build_module MP3-Cut-Gapless-0.03
            ;;  
        
        Template)
            build_module Template-Toolkit-2.21 - "TT_ACCEPT=y TT_EXAMPLES=n TT_EXTRAS=n"
            ;;
 
		# not adapted to buildit.sh
        DBD::mysql)
            # Build libmysqlclient
            tar jxvf mysql-5.1.37.tar.bz2
            cd mysql-5.1.37
            CC=gcc CXX=gcc \
            CFLAGS=" -fno-omit-frame-pointer $FLAGS" \
            CXXFLAGS=" -fno-omit-frame-pointer -felide-constructors -fno-exceptions -fno-rtti $FLAGS" \
                ./configure --prefix=$BUILD \
                --disable-dependency-tracking \
                --enable-thread-safe-client \
                --without-server --disable-shared --without-docs --without-man
            make
            if [ $? != 0 ]; then
                echo "make failed"
                exit $?
            fi
            make install
            cd ..
            rm -rf mysql-5.1.37

            # DBD::mysql custom, statically linked with libmysqlclient
            tar zxf DBD-mysql-3.0002.tar.gz
            cd DBD-mysql-3.0002
            cp -Rv ../hints .
            mkdir mysql-static
            cp $BUILD/lib/mysql/libmysqlclient.a mysql-static
            cd ..
            
            build_module DBD-mysql-3.0002 "--mysql_config=$BUILD/bin/mysql_config --libs=\"-Lmysql-static -lmysqlclient -lz -lm\" INSTALL_BASE=$PERL_BASE"
            ;;
        
        XML::Parser)
            build_expat           
            build_module XML-Parser-2.41 XML-Parser-2.41.patch "EXPATLIBPATH=$BUILD/lib EXPATINCPATH=$BUILD/include"
            ;;

        # not adapted to buildit.sh
        Font::FreeType)
            # build freetype
            tar zxf freetype-2.4.2.tar.gz
            cd freetype-2.4.2
            
            # Disable features we don't need for CODE2000
            cp -fv ../freetype-ftoption.h objs/ftoption.h
            
            # Disable modules we don't need for CODE2000
            cp -fv ../freetype-modules.cfg modules.cfg
            
            # libfreetype.a size (i386/x86_64 universal binary):
            #   1634288 (default)
            #    461984 (with custom ftoption.h/modules.cfg)
            
            CFLAGS="$FLAGS" \
            LDFLAGS="$FLAGS" \
				./configure --prefix=$BUILD $CROSS_OPTS
            $MAKE # needed for FreeBSD to use gmake 
            if [ $? != 0 ]; then
                echo "make failed"
                exit $?
            fi
            $MAKE install
            cd ..
            
            # Symlink static version of library to avoid OSX linker choosing dynamic versions
            cd build/lib
            ln -sf libfreetype.a libfreetype_s.a
            cd ../..

            tar zxf Font-FreeType-0.03.tar.gz
            cd Font-FreeType-0.03
            
            # Build statically
            patch -p0 < ../Font-FreeType-Makefile.patch
            
            # Disable some functions so we can compile out more freetype modules
            patch -p0 < ../Font-FreeType-lean.patch
            
            cp -Rv ../hints .
            cd ..
            
            build_module Font-FreeType-0.03
            
            ;;

        Media::Scan)            
			build_ffmpeg
			build_libexif
			build_libjpeg
			build_libpng
			build_giflib
			build_bdb
			build_libmediascan
            
            MSOPTS=" --with-static \
                --with-ffmpeg-includes=$BUILD/include \
                --with-lms-includes=$BUILD/include \
                --with-exif-includes=$BUILD/include \
                --with-jpeg-includes=$BUILD/include \
                --with-png-includes=$BUILD/include \
                --with-gif-includes=$BUILD/include \
                --with-bdb-includes=$BUILD/include"
			build_module libmediascan-0.1 - "$MSOPTS" bindings/perl   
            ;;
    esac
}

function merror() {
	echo "Error building $1"
	exit 1
}

# 1- tarball
# 2- patch
# 3- path/to/configure
# $OPT_CONF configure options
function build_tb() {
	tg=${1%%-*}
	if test -f .stamp-$tg; then return; fi
	
	td=${1%%.t*}
	echo ">>> Building $td..."
	CONFIGURE="./configure"
	if test -n "$3"; then CONFIGURE="$3"; fi

	if ! test -d $td; then
		comp=${1##*.}
		if test "$comp" = "gz"; then topt=xzf
		elif test "$comp" = "bz2"; then topt=xjf
		else merror $tg; fi
		tar $topt $1
		cd $td
		if test -f "../$2"; then patch -p1 < ../$2; fi
	else
		cd $td
		#if ! make clean; then merror $tg; fi
	fi

	if ! $CONFIGURE $OPT_CONF; then merror $tg; fi
	if ! make V=1; then merror $tg; fi
	if ! make V=1 install; then merror $tg; fi
    cd ..

	touch .stamp-$tg
}

function build_icu() {

	if test -f icu4c-4_6-src.tgz; then mv icu4c-4_6-src.tgz icu.tar.gz; fi
	
	OPT_CONF="$CROSS_OPTS --disable-shared --with-data-packaging=archive --with-cross-build=$ICU_HOST_DIR"
	CFLAGS="$CFLAGS -DU_USING_ICU_NAMESPACE=0" \
	CXXFLAGS="$CXXFLAGS -DU_USING_ICU_NAMESPACE=0" \
	build_tb icu.tar.gz - source/configure

	cd build/lib            
	ln -sf libicudata.a libicudata_s.a
	ln -sf libicui18n.a libicui18n_s.a
	ln -sf libicuuc.a libicuuc_s.a 
	cd ../..

	# Point to data directory for test suite
	export ICU_DATA=$BUILD/share/icu/4.6
	
	# Replace huge data file with smaller one containing only our collations
	rm -f $BUILD/share/icu/4.6/icudt46*.dat
	cp -v icudt46*.dat $BUILD/share/icu/4.6
}

function build_expat {
	OPT_CONF="$CROSS_OPTS --disable-shared"
	build_tb expat-2.0.1.tar.gz
	cd build/lib
	ln -sf libexpat.a libexpat_s.a
	cd ../..
}

function build_libexif {
	OPT_CONF="$CROSS_OPTS --disable-shared"
	build_tb libexif-0.6.20.tar.bz2
}    

function build_libjpeg {
	if test -f jpegsrc.v8b.tar.gz; then mv jpegsrc.v8b.tar.gz jpeg-8b.tar.gz; fi
	OPT_CONF="$CROSS_OPTS --disable-shared"
	build_tb jpeg-8b.tar.gz jpeg-8b.patch
}

function build_libpng {
	OPT_CONF="$CROSS_OPTS --disable-shared"
	build_tb libpng-1.4.3.tar.gz libpng-1.4.3.patch
}

function build_giflib {
	OPT_CONF="$CROSS_OPTS --disable-shared"
	build_tb giflib-4.1.6.tar.gz
}

function build_bdb {
	OPT_CONF="$CROSS_OPTS --disable-shared --with-cryptography=no -disable-hash --disable-queue \
		--disable-replication --disable-statistics --disable-verify --disable-posixmutexes \
		--disable-uimutexes --with-mutex=ARM/gcc-assembly"
	build_tb db-5.1.25.tar.gz - dist/configure
}

function build_libmediascan {
	OPT_CONF="$CROSS_OPTS"
	CFLAGS="$CFLAGS -I$BUILD/include" LDFLAGS="$LDFLAGS -L$BUILD/lib" LIBS="-lintl" build_tb libmediascan-0.1.tar.gz
}    

function build_ffmpeg {
	# HEY! THIS TOOK A WHILE to find out!!!
	# ffmpeg-0.8.4/libavcodec/arm/jrevdct_arm.S has absolute data memory references, 
	# can't be used as a shared library, objdump shows that TEXTREL is defined, 
	# and uclibc was build with FORCE_SHAREABLE_TEXT_SEGMENTS=y wich requires relocation!
	# so, disable arm assembly code :-( as I don't know how to fix that assembly code. 
	# its still there in ffmpeg-1.2.4

	OPT_CONF="--prefix=$BUILD \
		--disable-ffmpeg --disable-debug --disable-ffplay --disable-ffprobe --disable-ffserver \
        --disable-avdevice --enable-pic --disable-amd3dnow --disable-amd3dnowext --disable-mmx2 \
		--disable-sse --disable-ssse3 --disable-avx --disable-armv5te --disable-armv6 --disable-armv6t2 \
		--disable-armvfp --disable-iwmmxt --disable-mmi --disable-neon --disable-altivec \
		--disable-vis --enable-zlib --disable-bzlib \
        --disable-everything \
		--enable-swscale --enable-decoder=h264 --enable-decoder=mpeg1video --enable-decoder=mpeg2video \
        --enable-decoder=mpeg4 --enable-decoder=msmpeg4v1 --enable-decoder=msmpeg4v2 \
        --enable-decoder=msmpeg4v3 --enable-decoder=vp6f --enable-decoder=vp8 \
        --enable-decoder=wmv1 --enable-decoder=wmv2 --enable-decoder=wmv3 --enable-decoder=rawvideo \
        --enable-decoder=mjpeg --enable-decoder=mjpegb --enable-decoder=vc1 \
        --enable-decoder=aac --enable-decoder=ac3 --enable-decoder=dca --enable-decoder=mp3 \
        --enable-decoder=mp2 --enable-decoder=vorbis --enable-decoder=wmapro --enable-decoder=wmav1 \
		--enable-decoder=flv --enable-decoder=wmav2 --enable-decoder=wmavoice \
        --enable-decoder=pcm_dvd --enable-decoder=pcm_s16be --enable-decoder=pcm_s16le \
        --enable-decoder=pcm_s24be --enable-decoder=pcm_s24le \
        --enable-decoder=ass --enable-decoder=dvbsub --enable-decoder=dvdsub --enable-decoder=pgssub \
		--enable-decoder=xsub --enable-parser=aac --enable-parser=ac3 --enable-parser=dca \
		--enable-parser=h264 --enable-parser=mjpeg --enable-parser=mpeg4video --enable-parser=mpegaudio \
		--enable-parser=mpegvideo --enable-parser=vc1 \
        --enable-demuxer=asf --enable-demuxer=avi --enable-demuxer=flv --enable-demuxer=h264 \
        --enable-demuxer=matroska --enable-demuxer=mov --enable-demuxer=mpegps \
		--enable-demuxer=mpegts --enable-demuxer=mpegvideo --enable-protocol=file \
		--arch=arm --target-os=linux --enable-cross-compile --cross-prefix=${CROSS}- --disable-asm"
	build_tb ffmpeg-0.8.4.tar.bz2    
}

# Build a single module if requested, or all
if [ $1 ]; then
    build $1
else
    build_all
fi

# Reset PERL5LIB
export PERL5LIB=

# strip all so files
find $BUILD -name '*.so' -exec chmod u+w {} \;
find $BUILD -name '*.so' -exec strip {} \;

# clean out useless .bs/.packlist files, etc
find $BUILD -name '*.bs' -exec rm -f {} \;
find $BUILD -name '*.packlist' -exec rm -f {} \;

# create our directory structure
# rsync is used to avoid copying non-binary modules or other extra stuff
if [ "$PERL_512" -o "$PERL_514" -o "$PERL_516" -o "$PERL_518" -o "$PERL_520" ]; then
    # Check for Perl using use64bitint and add -64int
    ARCH=`$PERL_BIN -MConfig -le 'print $Config{archname}' | sed 's/gnu-//' | sed 's/^i[3456]86-/i386-/' | sed 's/armv5tejl/arm/' `
fi
mkdir -p $PERL_ARCH/$ARCH
rsync -amv --include='*/' --include='*.so' --include='*.bundle' --include='autosplit.ix' --exclude='*' $PERL_BASE/lib/perl5/*/auto $PERL_ARCH/$ARCH/
