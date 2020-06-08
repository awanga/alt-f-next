#############################################################
#
# bcrypt
#
############################################################

BCRYPT_VERSION = 3.1.4
BCRYPT_SOURCE = bcrypt-$(BCRYPT_VERSION).tar.gz
BCRYPT_SITE = https://pypi.python.org/packages/f3/ec/bb6b384b5134fd881b91b6aa3a88ccddaad0103857760711a5ab8c799358

BCRYPT_AUTORECONF = NO
BCRYPT_INSTALL_STAGING = NO
BCRYPT_INSTALL_TARGET = NO
BCRYPT_LIBTOOL_PATCH = NO

BCRYPT_DIR:=$(BUILD_DIR)/bcrypt-$(BCRYPT_VERSION)
BCRYPT_CAT:=$(ZCAT)

BCRYPT_BINARY:=_bcrypt.so
BCRYPT_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/bcrypt
BCRYPT_TARGET_BINARY:=$(BCRYPT_SITE_PACKAGE_DIR)/../$(BCRYPT_BINARY)

BCRYPT_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(BCRYPT_SOURCE):
	 $(call DOWNLOAD,$(BCRYPT_SITE),$(BCRYPT_SOURCE))

$(BCRYPT_DIR)/.unpacked: $(DL_DIR)/$(BCRYPT_SOURCE)
	$(BCRYPT_CAT) $(DL_DIR)/$(BCRYPT_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(BCRYPT_DIR)/.patched: $(BCRYPT_DIR)/.unpacked
	toolchain/patch-kernel.sh $(BCRYPT_DIR) package/bcrypt/ bcrypt-$(BCRYPT_VERSION)-\*.patch
	touch $@

# add DISTUTILS_DEBUG=1 to environment to debug setup.py
$(BCRYPT_DIR)/.build: $(BCRYPT_DIR)/.patched
	pip install cffi # shortcut to install cffi in HOST_DIR
	(cd $(BCRYPT_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(BCRYPT_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(BCRYPT_TARGET_BINARY): $(BCRYPT_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(BCRYPT_DIR)/dist/bcrypt-$(BCRYPT_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(BCRYPT_SITE_PACKAGE_DIR) -name \*.pyc -delete

bcrypt: uclibc python cffi $(TARGET_DIR)/$(BCRYPT_TARGET_BINARY)

bcrypt-unpack: $(BCRYPT_DIR)/.unpacked

bcrypt-build: $(BCRYPT_DIR)/.build

bcrypt-install: $(TARGET_DIR)/$(BCRYPT_TARGET_BINARY)

bcrypt-dirclean:
	rm -rf $(BCRYPT_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CFFI),y)
TARGETS+=bcrypt
endif
