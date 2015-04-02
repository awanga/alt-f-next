################################################################################
#
# librsync
#
################################################################################

LIBRSYNC_VERSION = 0.9.7
LIBRSYNC_SOURCE = librsync-$(LIBRSYNC_VERSION).tar.gz
LIBRSYNC_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/librsync/librsync/$(LIBRSYNC_VERSION)

LIBRSYNC_INSTALL_STAGING = YES
LIBRSYNC_INSTALL_TARGET = YES

LIBRSYNC_DEPENDENCIES = zlib bzip2 popt
LIBRSYNC_CONF_OPT = --disable-static --enable-shared

$(eval $(call AUTOTARGETS,package,librsync))

$(LIBRSYNC_HOOK_POST_INSTALL):
	$(RM) $(STAGING_DIR)/usr/bin/rdiff
	touch $@
