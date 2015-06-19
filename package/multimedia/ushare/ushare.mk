#############################################################
#
# uShare
#
#############################################################

USHARE_VERSION = 1.1a
USHARE_SOURCE = ushare-$(USHARE_VERSION).tar.bz2
USHARE_SITE = http://ushare.geexbox.org/releases/

USHARE_AUTORECONF = NO
USHARE_LIBTOOL_PATCH = NO

USHARE_DEPENDENCIES = uclibc libupnp libdlna

USHARE_CONF_OPT = --disable-static --cross-compile --cross-prefix=arm-linux-uclibcgnueabi- \
	--enable-dlna --with-libdlna-dir=$(STAGING_DIR)/usr/ \
	--with-libupnp-dir=$(STAGING_DIR)/usr/

$(eval $(call AUTOTARGETS,package/multimedia,ushare))

$(USHARE_TARGET_INSTALL_TARGET):
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(USHARE_DIR) install
	touch $@

$(USHARE_HOOK_POST_INSTALL):
	(cd $(TARGET_DIR); \
	rm -f etc/init.d/ushare; \
	)
	touch $@