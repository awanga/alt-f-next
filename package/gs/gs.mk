#############################################################
#
# gs
#
#############################################################

GS_VERSION = 8.71
GS_SOURCE = ghostscript-$(GS_VERSION).tar.gz
GS_SITE = http://downloads.sourceforge.net/project/ghostscript/
GS_AUTORECONF = YES
GS_LIBTOOL_PATCH = NO
GS_INSTALL_STAGING = YES
GS_INSTALL_TARGET = YES
GS_DEPENDENCIES = uclibc cups tiff jpeg libpng

#GS_CONF_ENV = CUPSCONFIG=$(STAGING_DIR)/usr/bin/cups-config

GS_CONF_OPT = --without-x --disable-cairo --disable-gtk --disable-fontconfig --with-system-libtiff --with-libiconv=gnu --without-jasper

$(eval $(call AUTOTARGETS,package,gs))

$(GS_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/ghostscript/8.71/examples $(TARGET_DIR)/usr/share/ghostscript/8.71/doc
	touch $@