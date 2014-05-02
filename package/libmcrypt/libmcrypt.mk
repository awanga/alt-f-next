#############################################################
#
# libmcrypt
#
#############################################################

LIBMCRYPT_VERSION = 2.5.8
LIBMCRYPT_SITE = $(BR2_SOURCEFORGE_MIRROR)/mcrypt/Libmcrypt/$(LIBMCRYPT_VERSION)
LIBMCRYPT_SOURCE = libmcrypt-$(LIBMCRYPT_VERSION).tar.bz2
LIBMCRYPT_INSTALL_STAGING = YES
LIBMCRYPT_DEPENDENCIES = uclibc 

$(eval $(call AUTOTARGETS,package,libmcrypt))

$(LIBMCRYPT_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/arm-linux-libmcrypt-config \
		$(TARGET_DIR)/usr/share/aclocal/libmcrypt.m4
	touch $@