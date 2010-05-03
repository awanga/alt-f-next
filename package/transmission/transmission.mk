#############################################################
#
# transmission
#
#############################################################
TRANSMISSION_VERSION = 1.92
TRANSMISSION_SOURCE = transmission-$(TRANSMISSION_VERSION).tar.bz2
TRANSMISSION_SITE = http://download.m0k.org/transmission/files
TRANSMISSION_AUTORECONF = NO
TRANSMISSION_INSTALL_STAGING = NO
TRANSMISSION_INSTALL_TARGET = YES
TRANSMISSION_LIBTOOL_PATCH = NO
TRANSMISSION_CONF_OPT = --disable-cli --disable-nls

TRANSMISSION_DEPENDENCIES = uclibc libcurl host-pkgconfig

$(eval $(call AUTOTARGETS,package,transmission))

$(TRANSMISSION_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/transmission-remote
	touch $@
