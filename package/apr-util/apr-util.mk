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
APR_UTIL_DEPENDENCIES = apr libiconv sqlite zlib expat db
APR_UTIL_CONF_OPT = \
	--with-apr=$(STAGING_DIR)/usr/bin/apr-1-config \
	--with-berkeley-db=$(STAGING_DIR)/usr --with-dbm=db48 \
	--with-iconv=$(STAGING_DIR)/usr \
	--with-expat=$(STAGING_DIR)/usr \
	--with-openssl=$(STAGING_DIR)/usr \
	--with-crypto --disable-static

#	--with-apr=$(APR_DIR) \
#	--with-apr=$(STAGING_DIR)/usr/bin/apr-1-config \

APR_UTIL_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
APR_UTIL_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) install

APR_UTIL_MAKE_OPT = -j1

$(eval $(call AUTOTARGETS,package,apr-util))

# cross-compile/stagind-dir HACKS!
$(APR_UTIL_TARGET_INSTALL_STAGING):
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(APR_UTIL_DIR) install
	sed -i 's|="/usr|="$(STAGING_DIR)/usr|' $(STAGING_DIR)/usr/bin/apu-1-config
	sed -i -e "s|^libdir=.*|libdir='$(STAGING_DIR)/usr/lib'|" \
		$(STAGING_DIR)/usr/lib/libaprutil-1.la
	touch $@

#		-e "/^dependency_libs=/s|/usr/lib/libapr-1.la|$(STAGING_DIR)/usr/lib/libapr-1.la|" \