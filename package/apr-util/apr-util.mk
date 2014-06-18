#############################################################
#
# apr-util
#
#############################################################

APR_UTIL_VERSION = 1.5.1
APR_UTIL_SITE = http://archive.apache.org/dist/apr
APR_UTIL_SOURCE = apr-util-$(APR_UTIL_VERSION).tar.gz

APR_UTIL_INSTALL_STAGING = YES
APR_UTIL_LIBTOOL_PATCH = NO
APR_UTIL_DEPENDENCIES = openssl libiconv sqlite zlib expat db apr

APR_UTIL_CONF_OPT = \
	--with-apr=$(STAGING_DIR)/usr/bin/apr-1-config \
	--with-berkeley-db=$(STAGING_DIR)/usr --with-dbm=db48 \
	--with-iconv=$(STAGING_DIR)/usr \
	--with-expat=$(STAGING_DIR)/usr \
	--with-openssl=$(STAGING_DIR)/usr \
	--with-crypto --disable-static

APR_UTIL_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
APR_UTIL_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) install

APR_UTIL_MAKE_OPT = -j1

$(eval $(call AUTOTARGETS,package,apr-util))

$(APR_UTIL_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/bin/apu-1-config \
		$(TARGET_DIR)/usr/lib/aprutil.exp
	touch $@

$(APR_UTIL_TARGET_INSTALL_STAGING):
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(APR_UTIL_DIR) install
	$(SED) "s|^prefix=.*|prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(STAGING_DIR)/usr/lib\'|g" \
		$(STAGING_DIR)/usr/bin/apu-1-config
	$(SED) "s|^libdir=.*|libdir='$(STAGING_DIR)/usr/lib'|" \
		$(STAGING_DIR)/usr/lib/libaprutil-1.la
	touch $@

