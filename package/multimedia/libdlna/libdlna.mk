#############################################################
#
# libdlna
#
#############################################################

LIBDLNA_VERSION = 0.2.4
LIBDLNA_SOURCE = libdlna-$(LIBDLNA_VERSION).tar.bz2
LIBDLNA_SITE = http://libdlna.geexbox.org/releases/

LIBDLNA_AUTORECONF = NO
LIBDLNA_LIBTOOL_PATCH = NO

LIBDLNA_INSTALL_STAGING = YES

LIBDLNA_DEPENDENCIES = uclibc ffmpeg

LIBDLNA_CONF_OPT = --disable-static --cross-compile --cross-prefix=arm-linux-uclibcgnueabi-

$(eval $(call AUTOTARGETS,package/multimedia,libdlna))

$(LIBDLNA_TARGET_INSTALL_TARGET):
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(LIBDLNA_DIR) install
	touch $@

$(LIBDLNA_TARGET_INSTALL_STAGING):
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(LIBDLNA_DIR) install
	touch $@
