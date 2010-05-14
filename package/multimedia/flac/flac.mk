################################################################################
#
# flac
#
################################################################################

FLAC_VERSION = 1.2.1
FLAC_SOURCE = flac-$(FLAC_VERSION).tar.gz
FLAC_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/flac/
FLAC_AUTORECONF = NO
FLAC_INSTALL_TARGET = YES
FLAC_INSTALL_STAGING = YES
FLAC_DEPENDENCIES = libogg

FLAC_CONF_OPT = \
	--enable-shared \
	--disable-cpplibs \
	--disable-xmms-plugin \
	--with-ogg=$(STAGING_DIR)/usr

$(eval $(call AUTOTARGETS,package/multimedia,flac))

$(FLAC_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/share/aclocal/libFLAC.m4
	touch $@