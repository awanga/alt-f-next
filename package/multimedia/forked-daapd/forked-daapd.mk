#############################################################
#
# forked-daapd
#
#############################################################

FORKED_DAAPD_VERSION = 0.19

# we want 0.19, not 0.19gcd
#FORKED_DAAPD_SOURCE = forked-daapd_$(FORKED_DAAPD_VERSION)gcd.orig.tar.gz
#FORKED_DAAPD_SITE = $(BR2_DEBIAN_MIRROR)/debian/pool/main/f/forked-daapd

FORKED_DAAPD_SOURCE = forked-daapd_$(FORKED_DAAPD_VERSION).orig.tar.gz
FORKED_DAAPD_SITE = http://backports.debian.org/debian-backports/pool/main/f/forked-daapd

FORKED_DAAPD_AUTORECONF = NO
FORKED_DAAPD_LIBTOOL_PATCH = NO

FORKED_DAAPD_INSTALL_STAGING = NO
FORKED_DAAPD_INSTALL_TARGET = YES

FORKED_DAAPD_DEPENDENCIES = uclibc zlib libavl libunistring libevent libgcrypt libconfuse mxml alsa-lib libantlr sqlite avahi ffmpeg taglib flac

FORKED_DAAPD_CONF_ENV = ZLIB_LIBS="-lz" ZLIB_CFLAGS=" " LIBS="-lstdc++"
FORKED_DAAPD_CONF_OPT = -localstatedir=/var --sysconfdir=/etc \
	--enable-flac --enable-musepack --disable-rpath

$(eval $(call AUTOTARGETS,package/multimedia,forked-daapd))
