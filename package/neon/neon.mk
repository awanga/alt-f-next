#############################################################
#
# neon
#
#############################################################

NEON_VERSION:=0.29.6

NEON_SITE:=http://www.webdav.org/neon/

NEON_LIBTOOL_PATCH:=NO
NEON_INSTALL_STAGING:=YES
NEON_INSTALL_TARGET_OPT:=DESTDIR=$(TARGET_DIR) install

NEON_CONF_OPT:=--enable-shared --without-gssapi --disable-rpath
NEON_DEPENDENCIES:=host-pkgconfig

ifeq ($(BR2_PACKAGE_NEON_LIBXML2),y)
NEON_CONF_OPT+=--with-libxml2=yes
NEON_CONF_OPT+=--with-expat=no
NEON_DEPENDENCIES+=libxml2
endif
ifeq ($(BR2_PACKAGE_NEON_ZLIB),y)
#NEON_CONF_OPT+=--with-zlib=$(STAGING_DIR)
NEON_CONF_OPT+=--with-zlib
NEON_DEPENDENCIES+=zlib
else
NEON_CONF_OPT+=--without-zlib
endif
ifeq ($(BR2_PACKAGE_NEON_EXPAT),y)
NEON_CONF_OPT+=--with-expat=$(STAGING_DIR)/usr/lib/libexpat.la
NEON_CONF_OPT+=--with-libxml2=no
NEON_DEPENDENCIES+=expat
endif
ifeq ($(BR2_PACKAGE_NEON_NOXML),y)
# webdav needs xml support
NEON_CONF_OPT+=--disable-webdav
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
NEON_CONF_OPT+=--with-ssl
NEON_DEPENDENCIES+=openssl
else
NEON_CONF_OPT+=--without-ssl
endif

$(eval $(call AUTOTARGETS,package,neon))

ifeq ($(BR2_ENABLE_DEBUG),)
# neon doesn't have an install-strip target, so do it afterwards
$(NEON_HOOK_POST_INSTALL): $(NEON_TARGET_INSTALL_TARGET)
	$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/libneon.so
	rm -f $(TARGET_DIR)/usr/bin/neon-config
	$(SED) "s|^prefix=.*|prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(STAGING_DIR)/usr/lib\'|g" \
		$(STAGING_DIR)/usr/bin/neon-config
	touch $@
endif
