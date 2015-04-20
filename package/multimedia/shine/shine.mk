################################################################################
#
# shine
#
################################################################################

SHINE_VERSION = 3.1.0
SHINE_SOURCE = shine-$(SHINE_VERSION).tar.gz
SHINE_SITE = https://github.com/savonet/shine/releases/download/$(SHINE_VERSION)

SHINE_AUTORECONF = NO
SHINE_LIBTOOL_PATCH = NO

SHINE_INSTALL_TARGET = YES
SHINE_INSTALL_STAGING = NO

SHINE_CONF_OPT = --disable-shared \

$(eval $(call AUTOTARGETS,package/multimedia,shine))

# $(SHINE_HOOK_POST_INSTALL):
# 	rm -f $(TARGET_DIR)/usr/share/aclocal/libFLAC.m4
# ifneq ($(BR2_PACKAGE_SHINE_PROGS),y)
# 	(cd $(TARGET_DIR)/usr/bin; rm -f $(SHINE_PROGS))
# endif
# 	touch $@