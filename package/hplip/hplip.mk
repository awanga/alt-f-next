#############################################################
#
# hplip
#
#############################################################

##########################################
#
# foomatic-db has to be build before hplip
#
##########################################

HPLIP_VERSION = 3.12.9
HPLIP_SOURCE = hplip-$(HPLIP_VERSION).tar.gz
HPLIP_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/hplip/hplip/$(HPLIP_VERSION)

HPLIP_AUTORECONF = NO
HPLIP_LIBTOOL_PATCH = NO
HPLIP_INSTALL_STAGING = NO
HPLIP_INSTALL_TARGET = YES

HPLIP_DEPENDENCIES = uclibc gs jpeg tiff libpng cups libusb netsnmp sane foomatic-db

HPLIP_CONF_OPT = --disable-doc-build --disable-qt3 \
	--disable-qt4 --disable-fax-build --disable-dbus-build \
	--enable-lite-build --enable-network-build --enable-scan-build \
	--enable-cups-ppd-install --enable-hpcups-install --enable-libusb01_build

$(eval $(call AUTOTARGETS,package,hplip))

$(HPLIP_HOOK_POST_CONFIGURE):
	sed -i 's/chgrp/echo/' $(HPLIP_DIR)/Makefile
	touch $@

$(HPLIP_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/etc/udev $(TARGET_DIR)/var/lib/hp
	touch $@
