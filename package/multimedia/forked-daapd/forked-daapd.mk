#############################################################
#
# forked-daapd
#
#############################################################

FORKED_DAAPD_VERSION = 23.0
FORKED_DAAPD_SOURCE = forked-daapd-$(FORKED_DAAPD_VERSION).tar.gz
FORKED_DAAPD_SITE = http://backports.debian.org/debian-backports/pool/main/f/forked-daapd

FORKED_DAAPD_AUTORECONF = NO
FORKED_DAAPD_LIBTOOL_PATCH = NO

FORKED_DAAPD_DEPENDENCIES = uclibc zlib libavl libunistring libevent2 libgcrypt libconfuse mxml alsa-lib libantlr sqlite avahi ffmpeg taglib flac gperf-host

FORKED_DAAPD_CONF_ENV = ZLIB_LIBS="-lz" ZLIB_CFLAGS=" "

FORKED_DAAPD_CONF_OPT = --localstatedir=/var --sysconfdir=/etc \
	--enable-flac --enable-musepack --disable-rpath

$(eval $(call AUTOTARGETS,package/multimedia,forked-daapd))

$(FORKED_DAAPD_HOOK_POST_EXTRACT):
	sed -i 's/@CONFUSE_CFLAGS@ @TAGLIB_CFLAGS@/& @LIBEVENT_CFLAGS@/' $(FORKED_DAAPD_DIR)/src/Makefile.am 
	sed -i 's/_EVENT_/EVENT__/' $(FORKED_DAAPD_DIR)/src/evrtsp/rtsp-libevent20.c
	find $(FORKED_DAAPD_DIR) -name \*.c | xargs sed -i 's/<config.h>/<config2.h>/'
	#aclocal -I ./m4
	#libtoolize --copy
	#autoconf
	#autoheader
	#automake --add-missing --copy --no-force
	touch $(FORKED_DAAPD_DIR)/configure
	chmod +x $(FORKED_DAAPD_DIR)/configure
	touch $@
