###########################################################
#
# wget
#
###########################################################

WGET_VERSION:=1.20.3
WGET_SOURCE:=wget-$(WGET_VERSION).tar.gz
WGET_SITE:=$(BR2_GNU_MIRROR)/wget

WGET_DIR:=$(BUILD_DIR)/wget-$(WGET_VERSION)
WGET_CAT:=$(ZCAT)
WGET_BINARY:=src/wget
WGET_TARGET_BINARY:=usr/bin/wget

WGET_CFLAGS = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_WGET_OPTIM)"

ifeq ($(BR2_PACKAGE_OPENSSL),n)
	DISABLE_SSL += --without-ssl
else
	DISABLE_SSL += --with-ssl=openssl
	WGET_DEPENDENCIES = openssl
endif

$(DL_DIR)/$(WGET_SOURCE):
	$(call DOWNLOAD,$(WGET_SITE),$(WGET_SOURCE))

wget-source: $(DL_DIR)/$(WGET_SOURCE)

$(WGET_DIR)/.unpacked: $(DL_DIR)/$(WGET_SOURCE)
	$(WGET_CAT) $(DL_DIR)/$(WGET_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	$(CONFIG_UPDATE) $(WGET_DIR)
	touch $@

#ac_cv_lib_pcre_pcre_compile=no \

$(WGET_DIR)/.configured: $(WGET_DIR)/.unpacked
	(cd $(WGET_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		$(WGET_CFLAGS) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--with-libssl-prefix=$(STAGING_DIR) \
		--prefix=/ \
		--disable-pcre \
		--with-included-libunistring \
		$(DISABLE_IPV6) \
		$(DISABLE_NLS) \
		$(DISABLE_SSL) \
	)
	touch $@

$(WGET_DIR)/$(WGET_BINARY): $(WGET_DIR)/.configured
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(WGET_DIR)

$(TARGET_DIR)/$(WGET_TARGET_BINARY): $(WGET_DIR)/$(WGET_BINARY)
	install -D $(WGET_DIR)/$(WGET_BINARY) $(TARGET_DIR)/$(WGET_TARGET_BINARY)

wget: uclibc $(WGET_DEPENDENCIES) $(TARGET_DIR)/$(WGET_TARGET_BINARY)

wget-patch: $(WGET_DIR)/.unpacked

wget-configure: $(WGET_DIR)/.configured

wget-build: $(WGET_DIR)/$(WGET_BINARY)

wget-clean:
	rm -f $(TARGET_DIR)/$(WGET_TARGET_BINARY)
	-$(MAKE) -C $(WGET_DIR) clean

wget-dirclean:
	rm -rf $(WGET_DIR)
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_WGET),y)
TARGETS+=wget
endif
