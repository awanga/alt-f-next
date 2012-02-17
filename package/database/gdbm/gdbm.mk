#############################################################
#
# gdbm
#
#############################################################
GDBM_VERSION = 1.8.3
GDBM_SOURCE = gdbm-$(GDBM_VERSION).tar.gz
GDBM_SITE = $(BR2_GNU_MIRROR)/gdbm
GDBM_AUTORECONF = NO
GDBM_INSTALL_STAGING = YES
GDBM_INSTALL_TARGET = YES
GDBM_LIBTOOL_PATCH = NO
GDBM_DIR = $(BUILD_DIR)/gdbm-$(GDBM_VERSION)
GDBM_CAT = $(ZCAT)
GDBM_BINARY = libgdbm.so.3.0.0
GDBM_TARGET_BINARY = usr/lib/$(GDBM_BINARY)

$(DL_DIR)/$(GDBM_SOURCE):
	$(call DOWNLOAD,$(GDBM_SITE),$(GDBM_SOURCE))

$(GDBM_DIR)/.unpacked: $(DL_DIR)/$(GDBM_SOURCE)
	$(GDBM_CAT) $(DL_DIR)/$(GDBM_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(GDBM_DIR)/.configured: $(GDBM_DIR)/.unpacked
	cat package/database/gdbm/gdbm-1.8.3.patch | patch -p1 -d $(GDBM_DIR)
	(cd $(GDBM_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--libdir=/usr/lib \
		--enable-shared \
		--disable-static \
	)
	touch $@

$(GDBM_DIR)/.libs/$(GDBM_BINARY): $(GDBM_DIR)/.configured
	$(MAKE) -C $(GDBM_DIR)

$(TARGET_DIR)/$(GDBM_TARGET_BINARY): $(GDBM_DIR)/.libs/$(GDBM_BINARY)
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(GDBM_DIR) install
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(GDBM_DIR) install

gdbm: uclibc $(TARGET_DIR)/$(GDBM_TARGET_BINARY)

gdbm-install: $(TARGET_DIR)/$(GDBM_TARGET_BINARY)

gdbm-build: $(GDBM_DIR)/.libs/$(GDBM_BINARY)

gdbm-source: $(DL_DIR)/$(GDBM_SOURCE)

gdbm-extract: $(GDBM_DIR)/.unpacked

gdbm-configure: $(GDBM_DIR)/.configured

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_GDBM),y)
TARGETS+=gdbm
endif
