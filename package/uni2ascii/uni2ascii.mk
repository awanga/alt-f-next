#############################################################
#
# uni2ascii
#
#############################################################

UNI2ASCII_VERSION = 4.18
UNI2ASCII_SITE = http://billposer.org/Software/Downloads
UNI2ASCII_SOURCE = uni2ascii-$(UNI2ASCII_VERSION).tar.bz2
UNI2ASCII_AUTORECONF = NO
UNI2ASCII_LIBTOOL_PATCH = YES
UNI2ASCII_INSTALL_STAGING = NO
UNI2ASCII_INSTALL_TARGET = YES
UNI2ASCII_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS,package,uni2ascii))

#$(UNI2ASCII_HOOK_POST_INSTALL):
#	rm -rf $(TARGET_DIR)/usr/share/uni2ascii
#	touch $@
