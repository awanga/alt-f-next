#!/usr/bin/env bash
#
# $Id$
#
# This script builds all binary Perl modules required by Squeezebox Server.
# 
# Supported OSes:
#
# Linux (Perl 5.8.8, 5.10.0, 5.12.4, 5.14.1, 5.16.3)
#   i386/x86_64 Linux
#   ARM Linux
#   PowerPC Linux
#   Sparc Linux (ReadyNAS)
# Mac OSX
#   Under 10.5, builds Universal Binaries for i386/ppc Perl 5.8.8
#   Under 10.6, builds Universal Binaries for i386/x86_64 Perl 5.10.0
#   Under 10.7, builds for x86_64 Perl 5.12.3 (Lion does not support 32-bit CPUs)
#   Under 10.9, builds for x86_64 Perl 5.16
#   Under 10.10, builds for x86_64 Perl 5.18
# FreeBSD 7.2 (Perl 5.8.9)
# FreeBSD 8.X,9.X (Perl 5.12.4)
#
# Perl 5.12.4/5.14.1 note:
#   You should build 5.12.4 using perlbrew and the following command. GCC's stack protector must be disabled
#   so the binaries will not be dynamically linked to libssp.so which is not available on some distros.
#   NOTE: On 32-bit systems for 5.12 and higher, -D use64bitint should be used. Debian Wheezy (the next release) will
#   use Perl 5.12.4 with use64bitint enabled, and hopefully other major distros will follow suit.
#
#     perlbrew install perl-5.12.4 -D usethreads -D use64bitint -A ccflags=-fno-stack-protector -A ldflags=-fno-stack-protector
#
#   For 64-bit native systems, use:
#
#     perlbrew install perl-5.12.4 -D usethreads -A ccflags=-fno-stack-protector -A ldflags=-fno-stack-protector
#

OS=`uname`
MACHINE=`uname -m`

# get system arch, stripping out extra -gnu on Linux
ARCH=`/usr/bin/perl -MConfig -le 'print $Config{archname}' | sed 's/gnu-//' | sed 's/^i[3456]86-/i386-/' | sed 's/armv5tejl/arm/' `

if [ $OS = "Linux" -o $OS = "Darwin" -o $OS = "FreeBSD" ]; then
    echo "Building for $OS / $ARCH"
else
    echo "Unsupported platform: $OS, please submit a patch or provide us with access to a development system."
    exit
fi

if [ ! -x /usr/bin/rsync ]; then
    echo "This script requires /usr/bin/rsync, please install it."
    exit
fi

# figure out OSX version and customize SDK options
OSX_VER=
OSX_FLAGS=
OSX_ARCH=
if [ $OS = "Darwin" ]; then
    OSX_VER=`/usr/sbin/system_profiler SPSoftwareDataType`
    REGEX=' OS X.* (10\.[5-9])'
    REGEX2=' OS X.* (10\.1[0])'

    if [[ $OSX_VER =~ $REGEX ]]; then
        OSX_VER=${BASH_REMATCH[1]}
    elif [[ $OSX_VER =~ $REGEX2 ]]; then
        OSX_VER=${BASH_REMATCH[1]}
    else
        echo "Unable to determine OSX version"
        exit 0
    fi
    
    if [ $OSX_VER = "10.5" ]; then
        # Leopard, build for i386/ppc with support back to 10.4
        OSX_ARCH="-arch i386 -arch ppc"
        OSX_FLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.4"
    elif [ $OSX_VER = "10.6" ]; then
        # Snow Leopard, build for x86_64/i386 with support back to 10.5
        OSX_ARCH="-arch x86_64 -arch i386"
        OSX_FLAGS="-isysroot /Developer/SDKs/MacOSX10.5.sdk -mmacosx-version-min=10.5"
    elif [ $OSX_VER = "10.7" ]; then
        # Lion, build for x86_64 with support back to 10.6
        OSX_ARCH="-arch x86_64"
        OSX_FLAGS="-isysroot /Developer/SDKs/MacOSX10.6.sdk -mmacosx-version-min=10.6"
    elif [ $OSX_VER = "10.9" ]; then
        # Mavericks, build for x86_64 with support back to 10.9
        OSX_ARCH="-arch x86_64"
        OSX_FLAGS="-mmacosx-version-min=10.9"
    elif [ $OSX_VER = "10.10" ]; then
        # Yosemite, build for x86_64 with support back to 10.10
        OSX_ARCH="-arch x86_64"
        OSX_FLAGS="-mmacosx-version-min=10.10"
    fi
fi

# Build dir
BUILD=$PWD/build
PERL_BASE=$BUILD/perl5x
PERL_ARCH=$BUILD/arch/perl5x

# Path to Perl 5.8.8
if [ -x "/usr/bin/perl5.8.8" ]; then
    PERL_58=/usr/bin/perl5.8.8
elif [ -x "/usr/local/bin/perl5.8.8" ]; then
    PERL_58=/usr/local/bin/perl5.8.8
elif [ -x "$HOME/perl5/perlbrew/perls/perl-5.8.9/bin/perl5.8.9" ]; then
    PERL_58=$HOME/perl5/perlbrew/perls/perl-5.8.9/bin/perl5.8.9
elif [ -x "/usr/local/bin/perl5.8.9" ]; then # FreeBSD 7.2
    PERL_58=/usr/local/bin/perl5.8.9
fi

if [ $PERL_58 ]; then
    echo "Building with Perl 5.8.x at $PERL_58"
    PERL_BIN=$PERL_58
    # Install dir for 5.8
    PERL_BASE=$BUILD/5.8
    PERL_ARCH=$BUILD/arch/5.8
fi


# Path to Perl 5.10.0
if [ -x "/usr/bin/perl5.10.0" ]; then
    PERL_510=/usr/bin/perl5.10.0
elif [ -x "/usr/local/bin/perl5.10.0" ]; then
    PERL_510=/usr/local/bin/perl5.10.0
elif [ -x "/usr/local/bin/perl5.10.1" ]; then # FreeBSD 8.2
    PERL_510=/usr/local/bin/perl5.10.1
fi

if [ $PERL_510 ]; then
    echo "Building with Perl 5.10 at $PERL_510"
    PERL_BIN=$PERL_510
    # Install dir for 5.10
    PERL_BASE=$BUILD/5.10
    PERL_ARCH=$BUILD/arch/5.10
fi

# Path to Perl 5.12
if [ "$OSX_VER" = "10.9" ]; then
    echo "Ignoring Perl 5.12 - we want 5.16 on Mavericks"
elif [ -x "/usr/bin/perl5.12.4" ]; then
    PERL_512=/usr/bin/perl5.12.4
elif [ -x "/usr/local/bin/perl5.12.4" ]; then
    PERL_512=/usr/local/bin/perl5.12.4
elif [ -x "/usr/local/bin/perl5.12.4" ]; then # Also FreeBSD 8.2
    PERL_512=/usr/local/bin/perl5.12.4
elif [ -x "$HOME/perl5/perlbrew/perls/perl-5.12.4/bin/perl5.12.4" ]; then
    PERL_512=$HOME/perl5/perlbrew/perls/perl-5.12.4/bin/perl5.12.4
elif [ -x "/usr/bin/perl5.12" ]; then
    # OSX Lion uses this path
    PERL_512=/usr/bin/perl5.12
fi

if [ $PERL_512 ]; then
    echo "Building with Perl 5.12 at $PERL_512"
    PERL_BIN=$PERL_512
    # Install dir for 5.12
    PERL_BASE=$BUILD/5.12
    PERL_ARCH=$BUILD/arch/5.12
fi

# Path to Perl 5.14.1
if [ -x "$HOME/perl5/perlbrew/perls/perl-5.14.1/bin/perl5.14.1" ]; then
    PERL_514=$HOME/perl5/perlbrew/perls/perl-5.14.1/bin/perl5.14.1
fi

if [ $PERL_514 ]; then
    echo "Building with Perl 5.14 at $PERL_514"
    PERL_BIN=$PERL_514
    # Install dir for 5.14
    PERL_BASE=$BUILD/5.14
    PERL_ARCH=$BUILD/arch/5.14
fi

# Path to Perl 5.16
if [ "$OSX_VER" = "10.10" ]; then
    echo "Ignoring Perl 5.16 - we want 5.18 on Yosemite"
elif [ -x "/usr/bin/perl5.16" ]; then
    PERL_516=/usr/bin/perl5.16
elif [ -x "/usr/bin/perl5.16.3" ]; then
    PERL_516=/usr/bin/perl5.16.3
fi

if [ $PERL_516 ]; then
    echo "Building with Perl 5.16 at $PERL_516"
    PERL_BIN=$PERL_516
    # Install dir for 5.16
    PERL_BASE=$BUILD/5.16
    PERL_ARCH=$BUILD/arch/5.16
fi

# Path to Perl 5.18
if [ -x "/usr/bin/perl5.18" ]; then
    PERL_518=/usr/bin/perl5.18
fi

# defined on the command line - no detection yet
if [ $PERL_518 ]; then
    echo "Building with Perl 5.18 at $PERL_518"
    PERL_BIN=$PERL_518
    # Install dir for 5.18
    PERL_BASE=$BUILD/5.18
    PERL_ARCH=$BUILD/arch/5.18
fi

# defined on the command line - no detection yet
if [ $PERL_520 ]; then
    echo "Building with Perl 5.20 at $PERL_520"
    PERL_BIN=$PERL_520
    # Install dir for 5.20
    PERL_BASE=$BUILD/5.20
    PERL_ARCH=$BUILD/arch/5.20
fi

# try to use default perl version
if [ "$PERL_BIN" = "" ]; then
    PERL_BIN=`which perl`
    PERL_VERSION=`perl -MConfig -le '$Config{version} =~ /(\d+.\d+)\./; print $1'`
    
    case "$PERL_VERSION" in
    "5.8")
        PERL_58=$PERL_BIN
        ;;
    "5.10")
        PERL_510=$PERL_BIN
        ;;
    "5.12")
        PERL_512=$PERL_BIN
        ;;
    "5.14")
        PERL_514=$PERL_BIN
        ;;
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

# Require modules to pass tests
RUN_TESTS=1

USE_HINTS=1

FLAGS="-fPIC"

# FreeBSD's make sucks
if [ $OS = "FreeBSD" ]; then
    if [ ! -x /usr/local/bin/gmake ]; then
        echo "ERROR: Please install GNU make (gmake)"
        exit
    fi
    export GNUMAKE=/usr/local/bin/gmake
    export MAKE=/usr/local/bin/gmake
else
    # Support a newer make if available, needed on ReadyNAS                                                                              
    if [ -x /usr/local/bin/make ]; then                                               
        export MAKE=/usr/local/bin/make                                         
    else                                                                           
        export MAKE=/usr/bin/make                        
    fi
fi

# Clean up
# XXX command-line flag to skip cleanup
rm -rf $BUILD/arch

mkdir $BUILD

# $1 = module to build
# $2 = Makefile.PL arg(s)
function build_module {
    if [ ! -d $1 ]; then

        if [ ! -f $1.tar.gz ]; then
            echo "ERROR: cannot find source code archive $1.tar.gz"
            echo "Please download all source files from http://github.com/Logitech/slimserver-vendor"
            exit
        fi

        tar zxvf $1.tar.gz
    fi

    cd $1
    
    if [ $USE_HINTS -eq 1 ]; then
        # Always copy in our custom hints for OSX
        cp -Rv ../hints .
    fi
    if [ $PERL_BIN ]; then
        export PERL5LIB=$PERL_BASE/lib/perl5
        
        $PERL_BIN Makefile.PL INSTALL_BASE=$PERL_BASE $2
        if [ $RUN_TESTS -eq 1 ]; then
            make test
        else
            make
        fi
        if [ $? != 0 ]; then
            if [ $RUN_TESTS -eq 1 ]; then
                echo "make test failed, aborting"
            else
                echo "make failed, aborting"
            fi
            exit $?
        fi
        make install
        make clean
    fi

    cd ..
    rm -rf $1
}

function build_all {
    build Audio::Scan
    build Class::C3::XS
    build Class::XSAccessor
    build Compress::Raw::Zlib
    build DBI
#   build DBD::mysql
    build DBD::SQLite
    build Digest::SHA1
    build EV
    build Encode::Detect
    build HTML::Parser
    # XXX - Image::Scale requires libjpeg-turbo - which requires nasm 2.07 or later (install from http://www.macports.org/)
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
            if [ $PERL_58 ]; then
                tar zxvf Class-C3-XS-0.11.tar.gz
                cd Class-C3-XS-0.11
                patch -p0 < ../Class-C3-XS-no-ckWARN.patch
                cp -Rv ../hints .
                export PERL5LIB=$PERL_BASE/lib/perl5

                $PERL_58 Makefile.PL INSTALL_BASE=$PERL_BASE $2
                if [ $RUN_TESTS -eq 1 ]; then
                    make test
                else
                    make
                fi
                if [ $? != 0 ]; then
                    if [ $RUN_TESTS -eq 1 ]; then
                        echo "make test failed, aborting"
                    else
                        echo "make failed, aborting"
                    fi
                    exit $?
                fi
                make install
                make clean
                cd ..
                rm -rf Class-C3-XS-0.11
            fi
            ;;
        
        Class::XSAccessor)
            if [ "$PERL_516" -o "$PERL_518" -o "$PERL_520" ]; then
                build_module Class-XSAccessor-1.18
            else
                build_module Class-XSAccessor-1.05
            fi
            ;;
        
        Compress::Raw::Zlib)
            if [ "$PERL_58" -o "$PERL_510" ]; then
	            build_module Compress-Raw-Zlib-2.033
            fi
            ;;
        
        DBI)
            if [ "$PERL_518" -o "$PERL_520" ]; then
                build_module DBI-1.628
            else
                build_module DBI-1.616
            fi
            ;;
        
        DBD::SQLite)
            RUN_TESTS=0
            if [ "$PERL_518" -o "$PERL_520" ]; then
                build_module DBI-1.628
            else
                build_module DBI-1.616
            fi
            RUN_TESTS=1
            
            # build ICU, but only if it doesn't exist in the build dir,
            # because it takes so damn long on slow platforms
            if [ ! -f build/lib/libicudata_s.a ]; then
                tar zxvf icu4c-4_6-src.tgz
                cd icu/source
                if [ $OS = 'Darwin' ]; then
                    ICUFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -DU_USING_ICU_NAMESPACE=0 -DU_CHARSET_IS_UTF8=1" # faster code for native UTF-8 systems
                    ICUOS="MacOSX"
                elif [ $OS = 'Linux' ]; then
                    ICUFLAGS="$FLAGS -DU_USING_ICU_NAMESPACE=0"
                    ICUOS="Linux"
                elif [ $OS = 'FreeBSD' ]; then
                    ICUFLAGS="$FLAGS -DU_USING_ICU_NAMESPACE=0"
                    ICUOS="FreeBSD"
                fi
                CFLAGS="$ICUFLAGS" CXXFLAGS="$ICUFLAGS" LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" \
                    ./runConfigureICU $ICUOS --prefix=$BUILD --enable-static --with-data-packaging=archive
                $MAKE
                if [ $? != 0 ]; then
                    echo "make failed"
                    exit $?
                fi
                $MAKE install
            
                cd ../..                
                rm -rf icu

                # Symlink static versions of libraries
                cd build/lib
                if [ $OS = 'FreeBSD' ]; then
                    # FreeBSD has different library names (?)
                    ln -sf libsicudata.a libicudata.a
                    ln -sf libsicui18n.a libicui18n.a
                    ln -sf libsicuuc.a libicuuc.a
                fi
            
                ln -sf libicudata.a libicudata_s.a
                ln -sf libicui18n.a libicui18n_s.a
                ln -sf libicuuc.a libicuuc_s.a 
                cd ../..
            fi
            
            # Point to data directory for test suite
            export ICU_DATA=$BUILD/share/icu/4.6
            
            # Replace huge data file with smaller one containing only our collations
            rm -f $BUILD/share/icu/4.6/icudt46*.dat
            cp -v icudt46*.dat $BUILD/share/icu/4.6
            
            # Custom build for ICU support
            tar zxvf DBD-SQLite-1.34_01.tar.gz
            cd DBD-SQLite-1.34_01
            patch -p0 < ../DBD-SQLite-ICU.patch
            cp -Rv ../hints .
            
            if [ $PERL_58 ]; then
                # Running 5.8
                export PERL5LIB=$PERL_BASE/lib/perl5

                $PERL_58 Makefile.PL INSTALL_BASE=$PERL_BASE $2

                if [ $OS = 'Darwin' ]; then
                    # OSX does not seem to properly find -lstdc++, so we need to hack the Makefile to add it
                    $PERL_58 -p -i -e "s{^LDLOADLIBS =.+}{LDLOADLIBS = -L$PWD/../build/lib -licudata_s -licui18n_s -licuuc_s -lstdc++}" Makefile
                fi

                $MAKE test
                if [ $? != 0 ]; then
                    echo "make test failed, aborting"
                    exit $?
                fi
                $MAKE install
                $MAKE clean
    
                cd ..
                rm -rf DBD-SQLite-1.34_01
            else
                cd ..
                if [ "$PERL_516" -o "$PERL_518" -o "$PERL_520" ]; then
                   RUN_TESTS=0
                fi
                build_module DBD-SQLite-1.34_01
                RUN_TESTS=1
            fi
            
            ;;
        
        Digest::SHA1)
            build_module Digest-SHA1-2.13
            ;;
        
        EV)
            build_module common-sense-2.0

            # custom build to apply pthread patch
            export PERL_MM_USE_DEFAULT=1
            
            tar zxvf EV-4.03.tar.gz
            cd EV-4.03
            patch -p0 < ../EV-llvm-workaround.patch # patch to avoid LLVM bug 9891
            if [ $OS = "Darwin" ]; then
                if [ $PERL_58 ]; then
                    patch -p0 < ../EV-fixes.patch # patch to disable pthreads and one call to SvREADONLY
                fi
            fi
            cp -Rv ../hints .
            cd ..
            
            build_module EV-4.03

            export PERL_MM_USE_DEFAULT=
            ;;
        
        Encode::Detect)
            build_module Data-Dump-1.19
            build_module ExtUtils-CBuilder-0.260301
            RUN_TESTS=0
            build_module Module-Build-0.35
            RUN_TESTS=1
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
            
            # build Image::Scale
            RUN_TESTS=0
            build_module Test-NoWarnings-1.02
            RUN_TESTS=1
            
            tar zxvf Image-Scale-0.08.tar.gz
            cd Image-Scale-0.08
            cp -Rv ../hints .
            cd ..
            
            build_module Image-Scale-0.08 "--with-jpeg-includes="$BUILD/include" --with-jpeg-static \
                    --with-png-includes="$BUILD/include" --with-png-static \
                    --with-gif-includes="$BUILD/include" --with-gif-static \
                    INSTALL_BASE=$PERL_BASE"
            
            ;;
        
        IO::AIO)
            if [ $OS != "FreeBSD" ]; then
                build_module common-sense-2.0
            
                # Don't use the darwin hints file, it breaks if compiled on Snow Leopard with 10.5 (!?)
                USE_HINTS=0
                RUN_TESTS=0
                build_module IO-AIO-3.71
                RUN_TESTS=1
                USE_HINTS=1
            fi
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
            if [ $OS = "Linux" ]; then
                build_module common-sense-2.0
                build_module Linux-Inotify2-1.21
            fi
            ;;
        
        Locale::Hebrew)
            build_module Locale-Hebrew-1.04
            ;;

        Mac::FSEvents)
            if [ $OS = 'Darwin' ]; then
                RUN_TESTS=0
                build_module Mac-FSEvents-0.04
                RUN_TESTS=1
            fi
            ;;
        
        Sub::Name)
            build_module Sub-Name-0.05
            ;;
        
        YAML::LibYAML)
            if [ "$PERL_516" -o "$PERL_518" -o "$PERL_520" ]; then
                RUN_TESTS=0
            fi
            build_module YAML-LibYAML-0.35
            RUN_TESTS=1
            ;;
        
        Audio::Scan)
            RUN_TESTS=0
            build_module Sub-Uplevel-0.22
            build_module Tree-DAG_Node-1.06
            build_module Test-Warn-0.23
            RUN_TESTS=1
            build_module Audio-Scan-0.93
            ;;

        MP3::Cut::Gapless)
            build_module Audio-Cuefile-Parser-0.02
            build_module MP3-Cut-Gapless-0.03
            ;;  
        
        Template)
            # Template, custom build due to 2 Makefile.PL's
            tar zxvf Template-Toolkit-2.21.tar.gz
            cd Template-Toolkit-2.21
            cp -Rv ../hints .
            cp -Rv ../hints ./xs
            cd ..

            make # minor test failure, so don't test
            RUN_TESTS=0
            build_module Template-Toolkit-2.21 "INSTALL_BASE=$PERL_BASE TT_ACCEPT=y TT_EXAMPLES=n TT_EXTRAS=n"
            RUN_TESTS=1

            ;;
        
        DBD::mysql)
            # Build libmysqlclient
            tar jxvf mysql-5.1.37.tar.bz2
            cd mysql-5.1.37
            CC=gcc CXX=gcc \
            CFLAGS="-O3 -fno-omit-frame-pointer $FLAGS $OSX_ARCH $OSX_FLAGS" \
            CXXFLAGS="-O3 -fno-omit-frame-pointer -felide-constructors -fno-exceptions -fno-rtti $FLAGS $OSX_ARCH $OSX_FLAGS" \
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
            tar zxvf DBD-mysql-3.0002.tar.gz
            cd DBD-mysql-3.0002
            cp -Rv ../hints .
            mkdir mysql-static
            cp $BUILD/lib/mysql/libmysqlclient.a mysql-static
            cd ..
            
            build_module DBD-mysql-3.0002 "--mysql_config=$BUILD/bin/mysql_config --libs=\"-Lmysql-static -lmysqlclient -lz -lm\" INSTALL_BASE=$PERL_BASE"
            
            ;;
        
        XML::Parser)
            # build expat
            tar zxvf expat-2.0.1.tar.gz
            cd expat-2.0.1
            CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" \
            LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" \
                ./configure --prefix=$BUILD \
                --disable-dependency-tracking
            make
            if [ $? != 0 ]; then
                echo "make failed"
                exit $?
            fi
            make install
            cd ..

            # Symlink static versions of libraries to avoid OSX linker choosing dynamic versions
            cd build/lib
            ln -sf libexpat.a libexpat_s.a
            cd ../..

            # XML::Parser custom, built against expat
            tar zxvf XML-Parser-2.41.tar.gz
            cd XML-Parser-2.41
            cp -Rv ../hints .
            cp -Rv ../hints ./Expat # needed for second Makefile.PL
            patch -p0 < ../XML-Parser-Expat-Makefile.patch
            
            cd ..
            
            build_module XML-Parser-2.41 "INSTALL_BASE=$PERL_BASE EXPATLIBPATH=$BUILD/lib EXPATINCPATH=$BUILD/include"
            
            rm -rf expat-2.0.1
            ;;
        
        Font::FreeType)
            # build freetype
            tar zxvf freetype-2.4.2.tar.gz
            cd freetype-2.4.2
            
            # Disable features we don't need for CODE2000
            cp -fv ../freetype-ftoption.h objs/ftoption.h
            
            # Disable modules we don't need for CODE2000
            cp -fv ../freetype-modules.cfg modules.cfg
            
            # libfreetype.a size (i386/x86_64 universal binary):
            #   1634288 (default)
            #    461984 (with custom ftoption.h/modules.cfg)
            
            CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" \
            LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" \
                ./configure --prefix=$BUILD
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

            tar zxvf Font-FreeType-0.03.tar.gz
            cd Font-FreeType-0.03
            
            # Build statically
            patch -p0 < ../Font-FreeType-Makefile.patch
            
            # Disable some functions so we can compile out more freetype modules
            patch -p0 < ../Font-FreeType-lean.patch
            
            cp -Rv ../hints .
            cd ..
            
            build_module Font-FreeType-0.03
            
            rm -rf freetype-2.4.2
            ;;
        
        Media::Scan)            
            build_ffmpeg
            build_libexif
            build_libjpeg
            build_libpng
            build_giflib
            build_bdb
            
            # build libmediascan
            # XXX library does not link correctly on Darwin with libjpeg due to missing x86_64
            # in libjpeg.dylib, Perl still links OK because it uses libjpeg.a
            tar zxvf libmediascan-0.1.tar.gz

            if [ $OSX_VER = "10.9" -o $OSX_VER = "10.10" ]; then
                patch -p0 libmediascan-0.1/bindings/perl/hints/darwin.pl < libmediascan-hints-darwin.pl.patch
            fi

            cd libmediascan-0.1
            CFLAGS="-I$BUILD/include $FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
            LDFLAGS="-L$BUILD/lib $FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
            OBJCFLAGS="-L$BUILD/lib $FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
                ./configure --prefix=$BUILD --disable-shared --disable-dependency-tracking
            make
            if [ $? != 0 ]; then
                echo "make failed"
                exit $?
            fi            
            make install
            cd ..

            # build Media::Scan
            cd libmediascan-0.1/bindings/perl
            # LMS's hints file is OK and also has custom frameworks added
            
            MSOPTS="--with-static \
                --with-ffmpeg-includes=$BUILD/include \
                --with-lms-includes=$BUILD/include \
                --with-exif-includes=$BUILD/include \
                --with-jpeg-includes=$BUILD/include \
                --with-png-includes=$BUILD/include \
                --with-gif-includes=$BUILD/include \
                --with-bdb-includes=$BUILD/include"
                
            if [ $PERL_BIN ]; then
                $PERL_BIN Makefile.PL $MSOPTS INSTALL_BASE=$PERL_BASE
                make
                if [ $? != 0 ]; then
                    echo "make failed, aborting"
                    exit $?
                fi
                # XXX hack until regular test works
                $PERL_BIN -Iblib/lib -Iblib/arch t/01use.t
                if [ $? != 0 ]; then
                    echo "make test failed, aborting"
                    exit $?
                fi
                make install
                make clean
            fi
            
            cd ../../..
            rm -rf libmediascan-0.1
            ;;
    esac
}

function build_libexif {
    if [ -f $BUILD/include/libexif/exif-data.h ]; then
        return
    fi
    
    # build libexif
    tar jxvf libexif-0.6.20.tar.bz2
    cd libexif-0.6.20
    
    CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
    LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
        ./configure --prefix=$BUILD \
        --disable-dependency-tracking
    $MAKE
    if [ $? != 0 ]; then
        echo "make failed"
        exit $?
    fi
    $MAKE install
    cd ..
    
    rm -rf libexif-0.6.20
}    

function build_libjpeg {
    if [ -f $BUILD/include/jpeglib.h ]; then
        return
    fi
    
    # build libjpeg-turbo on x86 platforms
    # skip on 10.9 until we've been able to build nasm from macports
    if [ $OS = "Darwin" -a $OSX_VER != "10.5" ]; then
        # Build i386/x86_64 versions of turbo
        tar zxvf libjpeg-turbo-1.1.1.tar.gz
        cd libjpeg-turbo-1.1.1
        
        # Disable features we don't need
        cp -fv ../libjpeg-turbo-jmorecfg.h jmorecfg.h
        
        # Build 64-bit fork
        CFLAGS="-O3 $OSX_FLAGS" \
        CXXFLAGS="-O3 $OSX_FLAGS" \
        LDFLAGS="$OSX_FLAGS" \
            ./configure --prefix=$BUILD --host x86_64-apple-darwin NASM=/usr/local/bin/nasm \
            --disable-dependency-tracking
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        cp -fv .libs/libjpeg.a libjpeg-x86_64.a
        
        # Build 32-bit fork
        make clean
        CFLAGS="-O3 -m32 $OSX_FLAGS" \
        CXXFLAGS="-O3 -m32 $OSX_FLAGS" \
        LDFLAGS="-m32 $OSX_FLAGS" \
            ./configure --prefix=$BUILD NASM=/usr/local/bin/nasm \
            --disable-dependency-tracking
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        cp -fv .libs/libjpeg.a libjpeg-i386.a
        
        # Combine the forks
        lipo -create libjpeg-x86_64.a libjpeg-i386.a -output libjpeg.a
        
        # Install and replace libjpeg.a with universal version
        make install
        cp -f libjpeg.a $BUILD/lib/libjpeg.a
        cd ..
    
    elif [ $OS = "Darwin" -a $OSX_VER = "10.5" ]; then
        # combine i386 turbo with ppc libjpeg
        
        # build i386 turbo
        tar zxvf libjpeg-turbo-1.1.1.tar.gz
        cd libjpeg-turbo-1.1.1
        
        # Disable features we don't need
        cp -fv ../libjpeg-turbo-jmorecfg.h jmorecfg.h
        
        CFLAGS="-O3 -m32 $OSX_FLAGS" \
        CXXFLAGS="-O3 -m32 $OSX_FLAGS" \
        LDFLAGS="-m32 $OSX_FLAGS" \
            ./configure --prefix=$BUILD NASM=/usr/local/bin/nasm \
            --disable-dependency-tracking
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        make install
        cp -fv .libs/libjpeg.a ../libjpeg-i386.a
        cd ..
        
        # build ppc libjpeg 6b
        tar zxvf jpegsrc.v6b.tar.gz
        cd jpeg-6b
        
        # Disable features we don't need
        cp -fv ../libjpeg62-jmorecfg.h jmorecfg.h
        
        CFLAGS="-arch ppc -O3 $OSX_FLAGS" \
        LDFLAGS="-arch ppc -O3 $OSX_FLAGS" \
            ./configure --prefix=$BUILD \
            --disable-dependency-tracking
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        cp -fv libjpeg.a ../libjpeg-ppc.a
        cd ..
        
        # Combine the forks
        lipo -create libjpeg-i386.a libjpeg-ppc.a -output libjpeg.a
        
        # Replace libjpeg library
        mv -fv libjpeg.a $BUILD/lib/libjpeg.a
        rm -fv libjpeg-i386.a libjpeg-ppc.a
        
    elif [ $ARCH = "i386-linux-thread-multi" -o $ARCH = "x86_64-linux-thread-multi" -o $OS = "FreeBSD" ]; then
        # build libjpeg-turbo
        tar zxvf libjpeg-turbo-1.1.1.tar.gz
        cd libjpeg-turbo-1.1.1
        
        # Disable features we don't need
        cp -fv ../libjpeg-turbo-jmorecfg.h jmorecfg.h
        
        CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" CXXFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS" \
            ./configure --prefix=$BUILD --disable-dependency-tracking
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        
        make install
        cd ..
        
    # build libjpeg v8 on other platforms
    else
        tar zxvf jpegsrc.v8b.tar.gz
        cd jpeg-8b
        
        # Disable features we don't need
        cp -fv ../libjpeg-jmorecfg.h jmorecfg.h
        
        CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
        LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
            ./configure --prefix=$BUILD \
            --disable-dependency-tracking
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        make install
        cd ..
    fi
    
    rm -rf jpeg-8b
    rm -rf jpeg-6b
    rm -rf libjpeg-turbo-1.1.1
}

function build_libpng {
    if [ -f $BUILD/include/png.h ]; then
        return
    fi
    
    # build libpng
    tar zxvf libpng-1.4.3.tar.gz
    cd libpng-1.4.3
    
    # Disable features we don't need
    cp -fv ../libpng-pngconf.h pngconf.h
    
    CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
    LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
        ./configure --prefix=$BUILD \
        --disable-dependency-tracking
    make && make check
    if [ $? != 0 ]; then
        echo "make failed"
        exit $?
    fi
    make install
    cd ..
    
    rm -rf libpng-1.4.3
}

function build_giflib {
    if [ -f $BUILD/include/gif_lib.h ]; then
        return
    fi
    
    # build giflib
    tar zxvf giflib-4.1.6.tar.gz
    cd giflib-4.1.6
    CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
    LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
        ./configure --prefix=$BUILD \
        --disable-dependency-tracking
    make
    if [ $? != 0 ]; then
        echo "make failed"
        exit $?
    fi
    make install
    cd ..
    
    rm -rf giflib-4.1.6
}

function build_ffmpeg {
    if [ -f $BUILD/include/libavformat/avformat.h ]; then
        return
    fi
    
    # build ffmpeg, enabling only the things libmediascan uses
    tar jxvf ffmpeg-0.8.4.tar.bz2
    cd ffmpeg-0.8.4
    
    if [ $MACHINE = "padre" ]; then
        patch -p0 < ../ffmpeg-padre-configure.patch
    fi
    
    echo "Configuring FFmpeg..."
    
    # x86: Disable all but the lowend MMX ASM
    # ARM: Disable all
    # PPC: Disable AltiVec
    FFOPTS="--prefix=$BUILD --disable-ffmpeg --disable-ffplay --disable-ffprobe --disable-ffserver \
        --disable-avdevice --enable-pic \
        --disable-amd3dnow --disable-amd3dnowext --disable-mmx2 --disable-sse --disable-ssse3 --disable-avx \
        --disable-armv5te --disable-armv6 --disable-armv6t2 --disable-armvfp --disable-iwmmxt --disable-mmi --disable-neon \
        --disable-altivec \
        --disable-vis \
        --enable-zlib --disable-bzlib \
        --disable-everything --enable-swscale \
        --enable-decoder=h264 --enable-decoder=mpeg1video --enable-decoder=mpeg2video \
        --enable-decoder=mpeg4 --enable-decoder=msmpeg4v1 --enable-decoder=msmpeg4v2 \
        --enable-decoder=msmpeg4v3 --enable-decoder=vp6f --enable-decoder=vp8 \
        --enable-decoder=wmv1 --enable-decoder=wmv2 --enable-decoder=wmv3 --enable-decoder=rawvideo \
        --enable-decoder=mjpeg --enable-decoder=mjpegb --enable-decoder=vc1 \
        --enable-decoder=aac --enable-decoder=ac3 --enable-decoder=dca --enable-decoder=mp3 \
        --enable-decoder=mp2 --enable-decoder=vorbis --enable-decoder=wmapro --enable-decoder=wmav1 --enable-decoder=flv \
        --enable-decoder=wmav2 --enable-decoder=wmavoice \
        --enable-decoder=pcm_dvd --enable-decoder=pcm_s16be --enable-decoder=pcm_s16le \
        --enable-decoder=pcm_s24be --enable-decoder=pcm_s24le \
        --enable-decoder=ass --enable-decoder=dvbsub --enable-decoder=dvdsub --enable-decoder=pgssub --enable-decoder=xsub \
        --enable-parser=aac --enable-parser=ac3 --enable-parser=dca --enable-parser=h264 --enable-parser=mjpeg \
        --enable-parser=mpeg4video --enable-parser=mpegaudio --enable-parser=mpegvideo --enable-parser=vc1 \
        --enable-demuxer=asf --enable-demuxer=avi --enable-demuxer=flv --enable-demuxer=h264 \
        --enable-demuxer=matroska --enable-demuxer=mov --enable-demuxer=mpegps --enable-demuxer=mpegts --enable-demuxer=mpegvideo \
        --enable-protocol=file"
    
    # ASM doesn't work right on x86_64
    # XXX test --arch options on Linux
    if [ $ARCH = "x86_64-linux-thread-multi" ]; then
        FFOPTS="$FFOPTS --disable-mmx"
    fi
    # FreeBSD amd64 needs arch option
    if [ $ARCH = "amd64-freebsd" ]; then
        FFOPTS="$FFOPTS --arch=x64"
    fi
    
    if [ $OS = "Darwin" ]; then
        SAVED_FLAGS=$FLAGS
        
        # Build 64-bit fork (10.6/10.7)
        if [ $OSX_VER != "10.5" ]; then
            FLAGS="-arch x86_64 -O3 -fPIC $OSX_FLAGS"      
            CFLAGS="$FLAGS" \
            LDFLAGS="$FLAGS" \
                ./configure $FFOPTS --arch=x86_64
        
            make
            if [ $? != 0 ]; then
                echo "make failed"
                exit $?
            fi
        
            cp -fv libavcodec/libavcodec.a libavcodec-x86_64.a
            cp -fv libavformat/libavformat.a libavformat-x86_64.a
            cp -fv libavutil/libavutil.a libavutil-x86_64.a
            cp -fv libswscale/libswscale.a libswscale-x86_64.a
        fi
        
        # Build 32-bit fork (all OSX versions)
        make clean
        FLAGS="-arch i386 -O3 $OSX_FLAGS"      
        CFLAGS="$FLAGS" \
        LDFLAGS="$FLAGS" \
            ./configure $FFOPTS --arch=x86_32
        
        make
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        
        cp -fv libavcodec/libavcodec.a libavcodec-i386.a
        cp -fv libavformat/libavformat.a libavformat-i386.a
        cp -fv libavutil/libavutil.a libavutil-i386.a
        cp -fv libswscale/libswscale.a libswscale-i386.a
        
        # Build PPC fork (10.5)
        if [ $OSX_VER = "10.5" ]; then
            make clean
            FLAGS="-arch ppc -O3 $OSX_FLAGS"      
            CFLAGS="$FLAGS" \
            LDFLAGS="$FLAGS" \
                ./configure $FFOPTS --arch=ppc --disable-altivec
        
            make
            if [ $? != 0 ]; then
                echo "make failed"
                exit $?
            fi
        
            cp -fv libavcodec/libavcodec.a libavcodec-ppc.a
            cp -fv libavformat/libavformat.a libavformat-ppc.a
            cp -fv libavutil/libavutil.a libavutil-ppc.a
            cp -fv libswscale/libswscale.a libswscale-ppc.a
        fi
        
        # Combine the forks
        if [ $OSX_VER = "10.5" ]; then
            lipo -create libavcodec-i386.a libavcodec-ppc.a -output libavcodec.a
            lipo -create libavformat-i386.a libavformat-ppc.a -output libavformat.a
            lipo -create libavutil-i386.a libavutil-ppc.a -output libavutil.a
            lipo -create libswscale-i386.a libswscale-ppc.a -output libswscale.a
        else
            lipo -create libavcodec-x86_64.a libavcodec-i386.a -output libavcodec.a
            lipo -create libavformat-x86_64.a libavformat-i386.a -output libavformat.a
            lipo -create libavutil-x86_64.a libavutil-i386.a -output libavutil.a
            lipo -create libswscale-x86_64.a libswscale-i386.a -output libswscale.a
        fi
        
        # Install and replace libs with universal versions
        make install
        cp -f libavcodec.a $BUILD/lib/libavcodec.a
        cp -f libavformat.a $BUILD/lib/libavformat.a
        cp -f libavutil.a $BUILD/lib/libavutil.a
        cp -f libswscale.a $BUILD/lib/libswscale.a
        
        FLAGS=$SAVED_FLAGS
        cd ..
    else           
        CFLAGS="$FLAGS -O3" \
        LDFLAGS="$FLAGS -O3" \
            ./configure $FFOPTS
        
        $MAKE
        if [ $? != 0 ]; then
            echo "make failed"
            exit $?
        fi
        $MAKE install
        cd ..
    fi
    
    rm -rf ffmpeg-0.8.4
}

function build_bdb {
    if [ -f $BUILD/include/db.h ]; then
        return
    fi
    
    # --enable-posixmutexes is needed to build on ReadyNAS Sparc.
    MUTEX=""
    if [ $MACHINE = "padre" ]; then
      MUTEX="--enable-posixmutexes"
    fi
    
    # build bdb
    tar zxvf db-5.1.25.tar.gz
    cd db-5.1.25/build_unix
    
    if [ $OS = "Darwin" ]; then
       pushd ..
       patch -p0 < ../db51-src_dbinc_atomic.patch
       popd
    fi

    CFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
    LDFLAGS="$FLAGS $OSX_ARCH $OSX_FLAGS -O3" \
        ../dist/configure --prefix=$BUILD $MUTEX \
        --with-cryptography=no -disable-hash --disable-queue --disable-replication --disable-statistics --disable-verify \
        --disable-dependency-tracking --disable-shared
    make
    if [ $? != 0 ]; then
        echo "make failed"
        exit $?
    fi
    make install
    cd ../..
    
    rm -rf db-5.1.25
}

# Build a single module if requested, or all
if [ $1 ]; then
    build $1
else
    build_all
fi

# Reset PERL5LIB
export PERL5LIB=

if [ $OS = 'Darwin' ]; then
    # strip -S on all bundle files
    find $BUILD -name '*.bundle' -exec chmod u+w {} \;
    find $BUILD -name '*.bundle' -exec strip -S {} \;
elif [ $OS = 'Linux' -o $OS = "FreeBSD" ]; then
    # strip all so files
    find $BUILD -name '*.so' -exec chmod u+w {} \;
    find $BUILD -name '*.so' -exec strip {} \;
fi

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

# could remove rest of build data, but let's leave it around in case
#rm -rf $PERL_BASE
#rm -rf $PERL_ARCH
#rm -rf $BUILD/bin $BUILD/etc $BUILD/include $BUILD/lib $BUILD/man $BUILD/share $BUILD/var
