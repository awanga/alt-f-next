#############################################################
#
# cffi
#
############################################################

CFFI_VERSION = 1.11.2
CFFI_SOURCE = cffi-$(CFFI_VERSION).tar.gz
CFFI_SITE = https://pypi.python.org/packages/c9/70/89b68b6600d479034276fed316e14b9107d50a62f5627da37fafe083fde3

CFFI_AUTORECONF = NO
CFFI_INSTALL_STAGING = NO
CFFI_INSTALL_TARGET = NO
CFFI_LIBTOOL_PATCH = NO

CFFI_DIR:=$(BUILD_DIR)/cffi-$(CFFI_VERSION)
CFFI_CAT:=$(ZCAT)

CFFI_BINARY:=_cffi_backend.so
CFFI_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/cffi
CFFI_TARGET_BINARY:=$(CFFI_SITE_PACKAGE_DIR)/../$(CFFI_BINARY)

CFFI_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(CFFI_SOURCE):
	 $(call DOWNLOAD,$(CFFI_SITE),$(CFFI_SOURCE))

$(CFFI_DIR)/.unpacked: $(DL_DIR)/$(CFFI_SOURCE)
	$(CFFI_CAT) $(DL_DIR)/$(CFFI_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(CFFI_DIR)/.patched: $(CFFI_DIR)/.unpacked
	toolchain/patch-kernel.sh $(CFFI_DIR) package/cffi/ cffi-$(CFFI_VERSION)-\*.patch
	touch $@

$(CFFI_DIR)/.build: $(CFFI_DIR)/.patched
	(cd $(CFFI_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(CFFI_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(CFFI_TARGET_BINARY): $(CFFI_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(CFFI_DIR)/dist/cffi-$(CFFI_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(CFFI_SITE_PACKAGE_DIR) -name \*.pyc -delete

cffi: uclibc python libffi $(TARGET_DIR)/$(CFFI_TARGET_BINARY)

cffi-unpack: $(CFFI_DIR)/.unpacked

cffi-build: $(CFFI_DIR)/.build

cffi-install: $(TARGET_DIR)/$(CFFI_TARGET_BINARY)

cffi-dirclean:
	rm -rf $(CFFI_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CFFI),y)
TARGETS+=cffi
endif
