#############################################################
#
# libusb
#
#############################################################

LIBUSB_VERSION:=0.1.12
LIBUSB_SOURCE:=libusb_$(LIBUSB_VERSION).orig.tar.gz
LIBUSB_SITE:=$(BR2_DEBIAN_MIRROR)/debian/pool/main/libu/libusb

LIBUSB_LIBTOOL_PATCH = NO
LIBUSB_INSTALL_STAGING = YES
LIBUSB_DEPENDENCIES = host-pkgconfig
LIBUSB_OPTS = --disable-build-docs

$(eval $(call AUTOTARGETS,package,libusb))

$(LIBUSB_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/libusb-config
	touch $@
