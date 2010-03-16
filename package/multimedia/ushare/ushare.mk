#############################################################
#
# uShare
#
#############################################################
USHARE_VERSION = 1.1a
USHARE_SOURCE = ushare-$(USHARE_VERSION).tar.bz2
USHARE_SITE = http://ushare.geexbox.org/releases/
USHARE_AUTORECONF = NO
USHARE_INSTALL_STAGING = NO
USHARE_INSTALL_TARGET = YES
USHARE_LIBTOOL_PATCH = NO
USHARE_DEPENDENCIES = uclibc libupnp

$(eval $(call AUTOTARGETS,package,ushare))

$(USHARE_HOOK_POST_EXTRACT):
	cat patches/ushare-1.1a.patch | patch -p0 -d $(USHARE_DIR)
	touch $@

$(USHARE_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/etc/init.d/ushare
	touch $@