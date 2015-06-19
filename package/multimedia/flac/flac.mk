################################################################################
#
# flac
#
################################################################################

FLAC_VERSION = 1.3.0
FLAC_SOURCE = flac-$(FLAC_VERSION).tar.xz
FLAC_SITE = http://downloads.xiph.org/releases/flac

FLAC_AUTORECONF = NO
FLAC_LIBTOOL_PATCH = NO

FLAC_INSTALL_STAGING = YES

FLAC_DEPENDENCIES = libogg
FLAC_PROGS = flac metaflac

FLAC_CONF_OPT = \
	--enable-shared \
	--disable-cpplibs \
	--disable-xmms-plugin \
	--with-ogg=$(STAGING_DIR)/usr

$(eval $(call AUTOTARGETS,package/multimedia,flac))

$(FLAC_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/share/aclocal/libFLAC.m4
ifneq ($(BR2_PACKAGE_FLAC_PROGS),y)
	(cd $(TARGET_DIR)/usr/bin; rm -f $(FLAC_PROGS))
endif
	touch $@