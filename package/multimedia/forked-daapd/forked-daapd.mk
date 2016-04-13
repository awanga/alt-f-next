#############################################################
#
# forked-daapd
#
#############################################################

FORKED_DAAPD_VERSION = 23.4
FORKED_DAAPD_SOURCE = forked-daapd-$(FORKED_DAAPD_VERSION).tar.gz
FORKED_DAAPD_SITE = https://github.com/ejurgensen/forked-daapd/archive

FORKED_DAAPD_AUTORECONF = YES
FORKED_DAAPD_LIBTOOL_PATCH = YES

FORKED_DAAPD_DEPENDENCIES = uclibc zlib libunistring libevent2 libgcrypt libconfuse mxml alsa-lib libantlr sqlite avahi ffmpeg gperf-host host-automake

FORKED_DAAPD_CONF_ENV = ZLIB_LIBS="-L$(STAGING_DIR)/usr/lib -lz" ZLIB_CFLAGS="-I$(STAGING_DIR)/usr/include"
# FIXME: zlib: install zlib.pc

FORKED_DAAPD_CONF_OPT = --localstatedir=/var --sysconfdir=/etc --enable-mpd --disable-rpath

$(eval $(call AUTOTARGETS,package/multimedia,forked-daapd))

$(FORKED_DAAPD_TARGET_SOURCE):
	$(call DOWNLOAD,$(FORKED_DAAPD_SITE),$(FORKED_DAAPD_VERSION).tar.gz)
	(cd $(DL_DIR); ln -sf $(FORKED_DAAPD_VERSION).tar.gz forked-daapd-$(FORKED_DAAPD_VERSION).tar.gz )
	mkdir -p $(BUILD_DIR)/forked-daapd-$(FORKED_DAAPD_VERSION)
	touch $@

$(FORKED_DAAPD_HOOK_POST_EXTRACT):
	sed -i 's/@CONFUSE_CFLAGS@ @TAGLIB_CFLAGS@/& @LIBEVENT_CFLAGS@/' $(FORKED_DAAPD_DIR)/src/Makefile.am 
	find $(FORKED_DAAPD_DIR) -name \*.c | xargs sed -i 's/<config.h>/<config2.h>/'
	##aclocal -I ./m4
	##libtoolize --copy
	##autoconf
	##autoheader
	##automake --add-missing --copy --no-force
	#touch $(FORKED_DAAPD_DIR)/configure
	#chmod +x $(FORKED_DAAPD_DIR)/configure
	sed -i 's/LT_INIT/AC_PROG_LIBTOOL\ndnl LT_INIT/' $(FORKED_DAAPD_DIR)/configure.ac
	touch $@
