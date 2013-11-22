#############################################################
#
# libmcrypt
#
#############################################################

LIBMCRYPT_VERSION = 2.5.8
LIBMCRYPT_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/mcrypt/Libmcrypt/$(LIBMCRYPT_VERSION)
LIBMCRYPT_SOURCE = libmcrypt-$(LIBMCRYPT_VERSION).tar.bz2
LIBMCRYPT_INSTALL_STAGING = YES
LIBMCRYPT_DEPENDENCIES = uclibc 

$(eval $(call AUTOTARGETS,package,libmcrypt))

