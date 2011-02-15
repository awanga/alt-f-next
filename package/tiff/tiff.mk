#############################################################
#
# tiff
#
#############################################################

TIFF_VERSION:=3.9.4
TIFF_SITE:=ftp://ftp.remotesensing.org/pub/libtiff
TIFF_SOURCE:=tiff-$(TIFF_VERSION).tar.gz
TIFF_LIBTOOL_PATCH = NO
TIFF_INSTALL_STAGING = YES
TIFF_INSTALL_TARGET = YES
TIFF_CONF_OPT = \
	--enable-shared \
	--disable-static \
	--without-x \
	--program-prefix=""

TIFF_DEPENDENCIES = uclibc host-pkgconfig zlib jpeg

$(eval $(call AUTOTARGETS,package,tiff))
