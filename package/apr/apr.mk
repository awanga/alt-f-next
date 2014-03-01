#############################################################
#
# apr
#
#############################################################

APR_VERSION = 1.4.6
APR_SITE = http://archive.apache.org/dist/apr
APR_SOURCE = apr-$(APR_VERSION).tar.gz

APR_INSTALL_STAGING = YES
APR_LIBTOOL_PATCH = NO

APR_DEPENDENCIES = libuuid

APR_CONF_ENV = \
	ac_cv_file__dev_zero=yes \
	ac_cv_func_setpgrp_void=yes \
	apr_cv_process_shared_works=yes \
	apr_cv_mutex_robust_shared=no \
	apr_cv_tcp_nodelay_with_cork=yes \
	ac_cv_sizeof_struct_iovec=8 \
	apr_cv_mutex_recursive=yes

APR_INSTALL_BUILD=/usr/share/apr-1/build
APR_CONF_OPT = --disable-static -with-installbuilddir=$(APR_INSTALL_BUILD)

APR_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
APR_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) install

$(eval $(call AUTOTARGETS,package,apr))

$(APR_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/bin/apr-1-config \
		$(TARGET_DIR)/usr/lib/apr.exp \
		$(TARGET_DIR)/usr/share/apr-1
	touch $@

$(APR_TARGET_INSTALL_STAGING):
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(APR_DIR) install
	$(SED) "s|^prefix=.*|prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(STAGING_DIR)/usr/lib\'|g" \
		-e "s|^installbuilddir=\"\(.*\)\"|installbuilddir=\'$(STAGING_DIR)\1\'|g" \
		$(STAGING_DIR)/usr/bin/apr-1-config
	$(SED) 's|apr_builddir=/|apr_builddir=$(STAGING_DIR)/|' \
		-e 's|top_builddir=/|top_builddir=$(STAGING_DIR)/|' \
		-e 's|apr_builders=/|apr_builders=$(STAGING_DIR)/|' \
		$(STAGING_DIR)/$(APR_INSTALL_BUILD)/apr_rules.mk
	$(SED) "s|^libdir=.*|libdir='$(STAGING_DIR)/usr/lib'|" $(STAGING_DIR)/usr/lib/libapr-1.la
	touch $@
