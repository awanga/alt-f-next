#############################################################
#
# libogg
#
#############################################################

LIBOGG_VERSION = 1.3.1
LIBOGG_SOURCE = libogg-$(LIBOGG_VERSION).tar.gz
LIBOGG_SITE = http://downloads.xiph.org/releases/ogg
LIBOGG_AUTORECONF = NO
LIBOGG_LIBTOOL_PATCH = NO
LIBOGG_INSTALL_STAGING = YES
LIBOGG_INSTALL_TARGET = YES

LIBOGG_DEPENDENCIES = uclibc host-pkgconfig

$(eval $(call AUTOTARGETS,package/multimedia,libogg))

$(LIBOGG_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/share/aclocal/ogg.m4
	touch $@