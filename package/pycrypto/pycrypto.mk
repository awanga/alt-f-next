#############################################################
#
# pycrypto
#
#############################################################

PYCRYPTO_VERSION = 2.6.1
PYCRYPTO_SOURCE = pycrypto-$(PYCRYPTO_VERSION).tar.gz
PYCRYPTO_SITE = https://ftp.dlitz.net/pub/dlitz/crypto/pycrypto

PYCRYPTO_AUTORECONF = NO
PYCRYPTO_INSTALL_STAGING = NO
PYCRYPTO_INSTALL_TARGET = NO
PYCRYPTO_LIBTOOL_PATCH = NO

PYCRYPTO_DIR:=$(BUILD_DIR)/pycrypto-$(PYCRYPTO_VERSION)
PYCRYPTO_CAT:=$(ZCAT)

PYCRYPTO_BINARY:=pycrypto.so
PYCRYPTO_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/Crypto
PYCRYPTO_TARGET_BINARY:=$(PYCRYPTO_SITE_PACKAGE_DIR)/../$(PYCRYPTO_BINARY)

PYCRYPTO_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(PYCRYPTO_SOURCE):
	 $(call DOWNLOAD,$(PYCRYPTO_SITE),$(PYCRYPTO_SOURCE))

$(PYCRYPTO_DIR)/.unpacked: $(DL_DIR)/$(PYCRYPTO_SOURCE)
	$(PYCRYPTO_CAT) $(DL_DIR)/$(PYCRYPTO_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(PYCRYPTO_DIR)/.patched: $(PYCRYPTO_DIR)/.unpacked
	toolchain/patch-kernel.sh $(PYCRYPTO_DIR) package/pycrypto/ pycrypto-$(PYCRYPTO_VERSION)-\*.patch
	touch $@

$(PYCRYPTO_DIR)/.configured: $(PYCRYPTO_DIR)/.patched
	(cd $(@D) && \
	$(TARGET_CONFIGURE_OPTS) \
	$(TARGET_CONFIGURE_ARGS) \
	./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--sysconfdir=/etc \
		--program-prefix="" \
	)
	touch $@

$(PYCRYPTO_DIR)/.build: $(PYCRYPTO_DIR)/.configured
	(cd $(PYCRYPTO_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(PYCRYPTO_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(PYCRYPTO_TARGET_BINARY): $(PYCRYPTO_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(PYCRYPTO_DIR)/dist/pycrypto-$(PYCRYPTO_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(PYCRYPTO_SITE_PACKAGE_DIR) -name \*.pyc -delete

pycrypto: uclibc python $(TARGET_DIR)/$(PYCRYPTO_TARGET_BINARY)

pycrypto-unpack: $(PYCRYPTO_DIR)/.unpacked

pycrypto-build: $(PYCRYPTO_DIR)/.build

pycrypto-install: $(TARGET_DIR)/$(PYCRYPTO_TARGET_BINARY)

pycrypto-dirclean:
	rm -rf $(PYCRYPTO_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_PYCRYPTO),y)
TARGETS+=pycrypto
endif
