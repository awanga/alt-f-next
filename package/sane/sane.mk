#############################################################
#
# sane
#
#############################################################

SANE_VERSION = 1.0.21
SANE_SOURCE = sane-backends-$(SANE_VERSION).tar.gz
SANE_SITE = http://alioth.debian.org/frs/download.php/3258/
SANE_AUTORECONF = NO
SANE_LIBTOOL_PATCH = YES
SANE_INSTALL_STAGING = YES
SANE_INSTALL_TARGET = YES
SANE_DEPENDENCIES = uclibc libusb jpeg tiff

SANE_CONF_OPT = --disable-latex --disable-translations --disable-ipv6 --disable-avahi --disable-rpath --with-pic --without-gphoto2

$(eval $(call AUTOTARGETS,package,sane))
