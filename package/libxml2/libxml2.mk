#############################################################
#
# libxml2
#
############################################################

LIBXML2_VERSION = 2.9.9
LIBXML2_SOURCE = libxml2-sources-$(LIBXML2_VERSION).tar.gz
LIBXML2_SITE = ftp://xmlsoft.org/libxml2

LIBXML2_INSTALL_STAGING = YES
LIBXML2_INSTALL_TARGET = YES
LIBXML2_LIBTOOL_PATCH = NO

LIBXML2_DEPENDENCIES = uclibc libxml2-host
LIBXML2_HOST_DEPENDENCIES = host-pkgconfig

LIBXML2_CONF_OPT = --with-gnu-ld --enable-shared --enable-static \
	--without-debugging --without-python --without-threads 

LIBXML2_HOST_CONF_OPT = --enable-shared --without-debugging \
	--without-python --without-threads

ifneq ($(BR2_LARGEFILE),y)
LIBXML2_CONF_ENV = CC="$(TARGET_CC) $(TARGET_CFLAGS) -DNO_LARGEFILE_SOURCE"
endif

ifeq ($(BR2_INET_IPV6),y)
LIBXML2_CONF_OPT += --enable-ipv6
else
LIBXML2_CONF_OPT += $(DISABLE_IPV6)
endif

$(eval $(call AUTOTARGETS,package,libxml2))

$(eval $(call AUTOTARGETS_HOST,package,libxml2))

$(LIBXML2_HOOK_POST_INSTALL):
	$(SED) "s|^prefix=.*|prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(STAGING_DIR)/usr/lib\'|g" \
		$(STAGING_DIR)/usr/bin/xml2-config
	rm -rf $(TARGET_DIR)/usr/share/aclocal \
	       $(TARGET_DIR)/usr/share/doc/libxml2-$(LIBXML2_VERSION) \
	       $(TARGET_DIR)/usr/share/gtk-doc \
	       $(TARGET_DIR)/usr/lib/cmake/libxml2/libxml2-config.cmake
	touch $@

$(LIBXML2_HOST_HOOK_POST_INSTALL):
	$(SED) "s|^prefix=.*|prefix=\'$(HOST_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(HOST_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(HOST_DIR)/usr/lib\'|g" \
		-e "s|echo -L${libdir}|echo $(HOST_RPATH) -L${libdir}|" \
		$(HOST_DIR)/usr/bin/xml2-config
	touch $@
