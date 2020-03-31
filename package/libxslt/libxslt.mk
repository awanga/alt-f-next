#############################################################
#
# libxslt
#
############################################################

#LIBXSLT_VERSION = 1.1.24
LIBXSLT_VERSION = 1.1.33
LIBXSLT_SOURCE = libxslt-$(LIBXSLT_VERSION).tar.gz
LIBXSLT_SITE = ftp://xmlsoft.org/libxslt

LIBXSLT_LIBTOOL_PATCH = NO
LIBXSLT_INSTALL_STAGING = YES
LIBXSLT_INSTALL_TARGET = YES
LIBXSLT_DEPENDENCIES = libxml2

# If we have enabled libgcrypt then use it, else disable crypto support.
ifeq ($(BR2_PACKAGE_LIBGCRYPT),y)
LIBXSLT_DEPENDENCIES += libgcrypt
else
LIBXSLT_XTRA_CONF_OPT = --without-crypto
endif

LIBXSLT_CONF_OPT = --with-gnu-ld --enable-shared \
		--enable-static $(LIBXSLT_XTRA_CONF_OPT) \
		$(DISABLE_NLS) $(DISABLE_IPV6) \
		--without-debugging --without-python \
		--without-threads \

LIBXSLT_CONF_ENV = XSLTPROC=/usr/bin/xsltproc LIBXML_CFLAGS=-I$(STAGING_DIR)/usr/include/libxml2
		
$(eval $(call AUTOTARGETS,package,libxslt))

$(LIBXSLT_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/xslt-config $(TARGET_DIR)/usr/lib/xsltConf.sh
	$(SED) "s,^prefix=.*,prefix=\'$(STAGING_DIR)/usr\',g" $(STAGING_DIR)/usr/bin/xslt-config
	$(SED) "s,^exec_prefix=.*,exec_prefix=\'$(STAGING_DIR)/usr\',g" $(STAGING_DIR)/usr/bin/xslt-config
	$(SED) "s,^includedir=.*,includedir=\'$(STAGING_DIR)/usr/include\',g" $(STAGING_DIR)/usr/bin/xslt-config
	touch $@

