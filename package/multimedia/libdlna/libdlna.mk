#############################################################
#
# libdlna
#
#############################################################
LIBDLNA_VERSION = 0.2.3
LIBDLNA_SOURCE = libdlna-$(LIBDLNA_VERSION).tar.bz2
LIBDLNA_SITE = http://libdlna.geexbox.org/releases/
LIBDLNA_AUTORECONF = NO
LIBDLNA_INSTALL_STAGING = YES
LIBDLNA_INSTALL_TARGET = YES
LIBDLNA_LIBTOOL_PATCH = NO
LIBDLNA_CONF_OPT = --disable-static \
	--cross-compile \
	--cross-prefix=arm-linux-uclibcgnueabi-

LIBDLNA_DEPENDENCIES = uclibc ffmpeg

$(eval $(call AUTOTARGETS,package/multimedia,libdlna))


$(LIBDLNA_TARGET_INSTALL_TARGET):
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(LIBDLNA_DIR) install
	touch $@

$(LIBDLNA_TARGET_INSTALL_STAGING):
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(LIBDLNA_DIR) install
	touch $@
