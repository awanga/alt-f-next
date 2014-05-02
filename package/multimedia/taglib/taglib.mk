#############################################################
#
# taglib
#
#############################################################

TAGLIB_VERSION = 1.6.3
TAGLIB_SOURCE = taglib-$(TAGLIB_VERSION).tar.gz
TAGLIB_SITE = http://taglib.github.io/releases

TAGLIB_LIBTOOL_PATCH = NO
TAGLIB_INSTALL_STAGING = YES

TAGLIB_DEPENDENCIES = uclibc

TAGLIB_CONF_ENV = \
	DO_NOT_COMPILE='bindings tests examples' \
	ac_cv_header_cppunit_extensions_HelperMacros_h=no \
	ac_cv_header_zlib_h=$(if $(BR2_PACKAGE_ZLIB),yes,no)

TAGLIB_CONF_OPT = --disable-libsuffix --program-prefix=''

$(eval $(call AUTOTARGETS,package/multimedia,taglib))

$(TAGLIB_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/taglib-config
	$(SED) "s|^prefix=.*|prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(STAGING_DIR)/usr/lib\'|g" \
		$(STAGING_DIR)/usr/bin/taglib-config
	touch $@
