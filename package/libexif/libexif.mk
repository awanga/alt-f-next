#############################################################
#
# libexif
#
#############################################################

LIBEXIF_VERSION = 0.6.21
LIBEXIF_SOURCE = libexif-$(LIBEXIF_VERSION).tar.bz2
LIBEXIF_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/libexif/libexif/$(LIBEXIF_VERSION)

LIBEXIF_AUTORECONF = NO
LIBEXIF_LIBTOOL_PATCH = NO

LIBEXIF_INSTALL_STAGING = YES
LIBEXIF_INSTALL_TARGET = YES

LIBEXIF_CONF_OPT = --disable-docs \
	--disable-nls \
	--disable-static \
	--without-libintl-prefix
	
LIBEXIF_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS,package,libexif))
