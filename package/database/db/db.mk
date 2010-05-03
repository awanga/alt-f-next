#############################################################
#
# db
#
#############################################################

DB_VERSION = 4.6.21
DB_SOURCE = db-$(DB_VERSION).tar.gz
#DB_SITE = http://www.oracle.com/database/berkeley-db/index.html
DB_SITE = http://download.oracle.com/berkeley-db
DB_LIBTOOL_PATCH = NO
DB_DEPENDENCIES = uclibc
DB_DIR = $(BUILD_DIR)/db-$(DB_VERSION)
DB_BUILD = $(BUILD_DIR)/db-$(DB_VERSION)/build_unix
DB_CAT = $(ZCAT)
DB_BINARY = db_verify
DB_TARGET_BINARY = usr/bin/$(DB_BINARY)

$(DL_DIR)/$(DB_SOURCE):
	$(call DOWNLOAD,$(DB_SITE),$(DB_SOURCE))

$(DB_DIR)/.unpacked: $(DL_DIR)/$(DB_SOURCE)
	$(DB_CAT) $(DL_DIR)/$(DB_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(DB_DIR)/.configured: $(DB_DIR)/.unpacked
	(cd $(DB_BUILD); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		../dist/configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--enable-shared \
		--disable-static \
		--enable-smallbuild \
	)
	touch $@

$(DB_BUILD)/$(DB_BINARY): $(DB_DIR)/.configured
	$(MAKE) -C $(DB_BUILD)

$(TARGET_DIR)/$(DB_TARGET_BINARY): $(DB_BUILD)/$(DB_BINARY)
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(DB_BUILD) install
	rm -rf $(TARGET_DIR)/usr/docs
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(DB_BUILD) install_include install_lib 

db: $(TARGET_DIR)/$(DB_TARGET_BINARY)

db-install: $(TARGET_DIR)/$(DB_TARGET_BINARY)

db-build: $(DB_BUILD)/$(DB_BINARY)

db-configure: $(DB_DIR)/.configured

db-extract: $(DB_DIR)/.unpacked

db-source: $(DL_DIR)/$(DB_SOURCE)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_DB),y)
TARGETS+=db
endif
