#############################################################
#
# hplip
#
#############################################################

HPLIP_VERSION = 3.10.5
HPLIP_SOURCE = hplip-$(HPLIP_VERSION).tar.gz
HPLIP_SITE = http://prdownloads.sourceforge.net/hplip/
HPLIP_AUTORECONF = NO
HPLIP_LIBTOOL_PATCH = YES
HPLIP_INSTALL_STAGING = NO
HPLIP_INSTALL_TARGET = YES
HPLIP_DEPENDENCIES = uclibc gs jpeg tiff libpng cups libusb netsnmp sane

HPLIP_CONF_OPT = --disable-qt3 --disable-qt4 --disable-gui-build --disable-dbus-build --disable-doc-build --enable-lite-build --disable-fax-build

$(eval $(call AUTOTARGETS,package,hplip))

$(HPLIP_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/etc/udev $(TARGET_DIR)/var/lib/hp
	touch @