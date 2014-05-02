#############################################################
#
# libpar2
#
#############################################################

LIBPAR2_VERSION = 0.2
LIBPAR2_SOURCE = libpar2-$(LIBPAR2_VERSION).tar.gz
LIBPAR2_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/parchive/libpar2/$(LIBPAR2_VERSION)

LIBPAR2_AUTORECONF = NO
LIBPAR2_INSTALL_STAGING = YES
LIBPAR2_INSTALL_TARGET = YES
LIBPAR2_LIBTOOL_PATCH = NO

LIBPAR2_DEPENDENCIES = uclibc libsigcpp

$(eval $(call AUTOTARGETS,package,libpar2))

$(LIBPAR2_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/lib/libpar2
	touch $@