#############################################################
#
# openssl
#
#############################################################

OPENSSL_VERSION:=1.0.2g
OPENSSL_SITE:=http://www.openssl.org/source

OPENSSL_MAKE = $(MAKE1)

# specific compiler optimization
OPENSSL_CFLAGS = $(TARGET_CFLAGS)
ifeq ($(BR2_PACKAGE_OPENSSL_SIZEOPTIM),y)
OPENSSL_CFLAGS = $(TARGET_CFLAGS) -Os
endif

# Some architectures are optimized in OpenSSL
OPENSSL_TARGET_ARCH=generic32
ifeq ($(ARCH),avr32)
OPENSSL_TARGET_ARCH=avr32
endif
ifeq ($(ARCH),ia64)
OPENSSL_TARGET_ARCH=ia64
endif
ifeq ($(ARCH),powerpc)
OPENSSL_TARGET_ARCH=ppc
endif
ifeq ($(ARCH),x86_64)
OPENSSL_TARGET_ARCH=x86_64
endif

OPENSSL_INSTALL_STAGING = YES
OPENSSL_INSTALL_STAGING_OPT = INSTALL_PREFIX=$(STAGING_DIR) install
OPENSSL_INSTALL_TARGET_OPT = INSTALL_PREFIX=$(TARGET_DIR) install_sw

OPENSSL_DEPENDENCIES = zlib

ifeq ($(BR2_PACKAGE_CRYPTODEV),y)
	OPENSSL_DEPENDENCIES += cryptodev
	OPENSSL_CRYPTO_OPT = -DHAVE_CRYPTODEV -DUSE_CRYPTODEV_DIGESTS -DHASH_MAX_LEN=64
	OPENSSL_CFLAGS += $(OPENSSL_CRYPTO_OPT)
endif

$(eval $(call AUTOTARGETS,package,openssl))

$(OPENSSL_TARGET_CONFIGURE):
	(cd $(OPENSSL_DIR); \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		./Configure \
			$(OPENSSL_CRYPTO_OPT) \
			-DOPENSSL_SMALL_FOOTPRINT \
			--prefix=/usr \
			--openssldir=/etc/ssl \
			threads shared \
			no-idea no-md2 no-mdc2 no-rc5 no-camellia no-seed \
			no-krb5 no-jpake no-store no-hw no-zlib \
			no-ssl2 no-ssl3 no-comp no-err no-engines \
			linux-$(OPENSSL_TARGET_ARCH) \
	)
	touch $@

$(OPENSSL_TARGET_BUILD):
	# libs compiled with chosen optimization
	$(SED) "s:-O[0-9]:$(OPENSSL_CFLAGS):" $(OPENSSL_DIR)/Makefile
	$(OPENSSL_MAKE) CC=$(TARGET_CC) MAKEDEPPROG=$(TARGET_CC) -C $(OPENSSL_DIR) depend build_crypto build_ssl build_engines
	# openssl program compiled with -Os, saves 27KB
	$(SED) "s:-O[0-9]:-Os:" $(OPENSSL_DIR)/Makefile
	$(OPENSSL_MAKE) CC=$(TARGET_CC) MAKEDEPPROG=$(TARGET_CC) -C $(OPENSSL_DIR) build_apps
	touch $@

$(OPENSSL_HOOK_POST_INSTALL):
	$(if $(BR2_HAVE_DEVFILES),,rm -rf $(TARGET_DIR)/usr/lib/ssl)
ifeq ($(BR2_PACKAGE_OPENSSL_BIN),y)
	$(STRIPCMD) $(STRIP_STRIP_ALL) $(TARGET_DIR)/usr/bin/openssl
else
	rm -f $(TARGET_DIR)/usr/bin/openssl
endif
	rm -f $(TARGET_DIR)/usr/bin/c_rehash
	# libraries gets installed read only, so strip fails
	for i in $(addprefix $(TARGET_DIR)/usr/lib/,libcrypto.so.* libssl.so.*); \
	do chmod +w $$i; $(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $$i; done
ifneq ($(BR2_PACKAGE_OPENSSL_ENGINES),y)
	rm -rf $(TARGET_DIR)/usr/lib/engines
else
	chmod +w $(TARGET_DIR)/usr/lib/engines/lib*.so
	$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/engines/lib*.so
endif
	touch $@

$(OPENSSL_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	rm -rf $(addprefix $(TARGET_DIR)/,etc/ssl usr/bin/openssl usr/include/openssl)
	rm -rf $(addprefix $(TARGET_DIR)/usr/lib/,ssl engines libcrypto* libssl* pkgconfig/libcrypto.pc)
	rm -rf $(addprefix $(STAGING_DIR)/,etc/ssl usr/bin/openssl usr/include/openssl)
	rm -rf $(addprefix $(STAGING_DIR)/usr/lib/,ssl engines libcrypto* libssl* pkgconfig/libcrypto.pc)
	rm -f $(OPENSSL_TARGET_INSTALL_TARGET) $(OPENSSL_HOOK_POST_INSTALL)
