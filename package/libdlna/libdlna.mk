#############################################################
#
# libdlna
#
#############################################################
LIBDLNA_VERSION = 0.2.3
LIBDLNA_SOURCE = libdlna-$(LIBDLNA_VERSION).tar.bz2
LIBDLNA_SITE = http://libdlna.geexbox.org/releases/libdlna-$(LIBDLNA_VERSION).tar.bz2
LIBDLNA_AUTORECONF = NO
LIBDLNA_INSTALL_STAGING = YES
LIBDLNA_INSTALL_TARGET = YES
LIBDLNA_LIBTOOL_PATCH = NO
LIBDLNA_CONF_OPT =  --disable-nls --disable-gtk

LIBDLNA_DEPENDENCIES = uclibc libavformat libavcodec

$(eval $(call AUTOTARGETS,package,libdlna))

#$(LIBDLNA_HOOK_POST_INSTALL):
#	rm -f $(TARGET_DIR)/usr/bin/libdlnacli \
#		$(TARGET_DIR)/usr/bin/libdlna-remote
#	touch $@
