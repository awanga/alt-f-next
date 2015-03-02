#############################################################
#
# libusb1
#
#############################################################

LIBUSB1_VERSION:=1.0.19
LIBUSB1_SOURCE:=libusb-$(LIBUSB1_VERSION).tar.bz2
LIBUSB1_SITE:= $(BR2_SOURCEFORGE_MIRROR)/project/libusb/libusb-1.0/libusb-$(LIBUSB1_VERSION)

LIBUSB1_LIBTOOL_PATCH = NO
LIBUSB1_INSTALL_STAGING = YES

LIBUSB1_CONF_OPT = --disable-udev --disable-static --enable-system-log

$(eval $(call AUTOTARGETS,package,libusb1))
