#############################################################
#
# forked-daapd
#
#############################################################
FORKED_DAAPD_VERSION = 0.12
FORKED_DAAPD_SOURCE = forked-daapd-$(FORKED_DAAPD_VERSION).tar.gz
FORKED_DAAPD_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/mt-daapd/
FORKED_DAAPD_AUTORECONF = NO
FORKED_DAAPD_INSTALL_STAGING = NO
FORKED_DAAPD_INSTALL_TARGET = YES
FORKED_DAAPD_LIBTOOL_PATCH = NO
	
FORKED_DAAPD_DEPENDENCIES = uclibc zlib libavl libunistring libevent libgcrypt libconfuse mxml alsa-lib libantlr sqlite avahi ffmpeg taglib flac

FORKED_DAAPD_CONF_ENV = ZLIB_LIBS="-lz" ZLIB_CFLAGS=" " LIBS="-lstdc++"
FORKED_DAAPD_CONF_OPT = -localstatedir=/var --sysconfdir=/etc \
	--enable-flac --enable-musepack

$(eval $(call AUTOTARGETS,package/multimedia,forked-daapd))
