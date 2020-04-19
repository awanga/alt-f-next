#############################################################
#
# usbutils
#
#############################################################

USBUTILS_VERSION:=0.87-1
USBUTILS_SOURCE:=usbutils_$(USBUTILS_VERSION).orig.tar.gz
USBUTILS_SITE:=http://archive.debian.org/debian/pool/main/u/usbutils

USBUTILS_LIBTOOL_PATCH = NO
USBUTILS_DEPENDENCIES = libusb
USBID_SITE="http://www.linux-usb.org/usb.ids.gz"

$(eval $(call AUTOTARGETS,package,usbutils))

$(USBUTILS_HOOK_POST_INSTALL):
	wget -N -P $(TARGET_DIR)/usr/share $(USBID_SITE)
	rm -rf $(TARGET_DIR)/usr/share/pkgconfig \
		$(TARGET_DIR)/usr/bin/usb-devices \
		$(TARGET_DIR)/usr/sbin/update-usbids.sh
	touch $@
