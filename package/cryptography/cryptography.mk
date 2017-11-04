#############################################################
#
# cryptography
#
############################################################

CRYPTOGRAPHY_VERSION = 2.1.2
CRYPTOGRAPHY_SOURCE = cryptography-$(CRYPTOGRAPHY_VERSION).tar.gz
CRYPTOGRAPHY_SITE = https://pypi.python.org/packages/78/62/9e38f9b22efe08ec2b40a56c0f46848ce03c35fdd6e78ae445589f914462

CRYPTOGRAPHY_AUTORECONF = NO
CRYPTOGRAPHY_INSTALL_STAGING = NO
CRYPTOGRAPHY_INSTALL_TARGET = NO
CRYPTOGRAPHY_LIBTOOL_PATCH = NO

CRYPTOGRAPHY_DIR:=$(BUILD_DIR)/cryptography-$(CRYPTOGRAPHY_VERSION)
CRYPTOGRAPHY_CAT:=$(ZCAT)

CRYPTOGRAPHY_BINARY:=_openssl.so
CRYPTOGRAPHY_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/cryptography
CRYPTOGRAPHY_TARGET_BINARY:=$(CRYPTOGRAPHY_SITE_PACKAGE_DIR)/../$(CRYPTOGRAPHY_BINARY)

CRYPTOGRAPHY_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(CRYPTOGRAPHY_SOURCE):
	 $(call DOWNLOAD,$(CRYPTOGRAPHY_SITE),$(CRYPTOGRAPHY_SOURCE))

$(CRYPTOGRAPHY_DIR)/.unpacked: $(DL_DIR)/$(CRYPTOGRAPHY_SOURCE)
	$(CRYPTOGRAPHY_CAT) $(DL_DIR)/$(CRYPTOGRAPHY_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(CRYPTOGRAPHY_DIR)/.patched: $(CRYPTOGRAPHY_DIR)/.unpacked
	toolchain/patch-kernel.sh $(CRYPTOGRAPHY_DIR) package/cryptography/ cryptography-$(CRYPTOGRAPHY_VERSION)-\*.patch
	touch $@

$(CRYPTOGRAPHY_DIR)/.build: $(CRYPTOGRAPHY_DIR)/.patched
	pip install cffi  # shortcut to install cffi in HOST_DIR
	(cd $(CRYPTOGRAPHY_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(CRYPTOGRAPHY_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(CRYPTOGRAPHY_TARGET_BINARY): $(CRYPTOGRAPHY_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(CRYPTOGRAPHY_DIR)/dist/cryptography-$(CRYPTOGRAPHY_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(CRYPTOGRAPHY_SITE_PACKAGE_DIR) -name \*.pyc -delete

cryptography: uclibc python $(TARGET_DIR)/$(CRYPTOGRAPHY_TARGET_BINARY)

cryptography-unpack: $(CRYPTOGRAPHY_DIR)/.unpacked

cryptography-build: $(CRYPTOGRAPHY_DIR)/.build

cryptography-install: $(TARGET_DIR)/$(CRYPTOGRAPHY_TARGET_BINARY)

cryptography-dirclean:
	rm -rf $(CRYPTOGRAPHY_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CFFI),y)
TARGETS+=cryptography
endif
