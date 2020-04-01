#############################################################
#
# libiconv
#
############################################################

LIBICONV_VERSION = 1.16
LIBICONV_SOURCE = libiconv-$(LIBICONV_VERSION).tar.gz
LIBICONV_SITE = $(BR2_GNU_MIRROR)/libiconv

LIBICONV_AUTORECONF = NO
LIBICONV_LIBTOOL_PATCH = NO
LIBICONV_INSTALL_STAGING = YES
LIBICONV_INSTALL_TARGET = YES

LIBICONV_DEPENDENCIES = uclibc

LIBICONV_CONF_OPT = --libdir=/usr/lib
LIBICONV_CONF_ENV = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_LIBICONV_OPTIM)"

ifeq ($(BR2_ENABLE_DEBUG),y)
LIBICONV_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
else
LIBICONV_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install-strip STRIPPROG="$(STRIPCMD)"
endif

$(eval $(call AUTOTARGETS,package,libiconv))

# a patch in uClibc removes iconv.h:
ifeq ($(BR2_PACKAGE_LIBICONV),y)
TARGETS := $(STAGING_DIR)/usr/include/iconv.h $(TARGETS)
endif

$(STAGING_DIR)/usr/include/iconv.h: libiconv-install-staging
	cp $(LIBICONV_DIR)/include/iconv.h.inst $(STAGING_DIR)/usr/include/iconv.h
	touch $@

$(LIBICONV_HOOK_POST_INSTALL):
	# Remove not used preloadable libiconv.so
	rm -f $(STAGING_DIR)/usr/lib/preloadable_libiconv.so
	rm -f $(TARGET_DIR)/usr/lib/preloadable_libiconv.so
ifneq ($(BR2_ENABLE_DEBUG),y)
	$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/libiconv.so.*
	$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/libcharset.so.*
endif
	touch $@
