#############################################################
#
# pynacl
#
############################################################

PYNACL_VERSION = 1.1.2
PYNACL_SOURCE = $(PYNACL_VERSION).tar.gz
PYNACL_SITE = https://github.com/pyca/pynacl/archive

PYNACL_AUTORECONF = NO
PYNACL_INSTALL_STAGING = NO
PYNACL_INSTALL_TARGET = NO
PYNACL_LIBTOOL_PATCH = NO

PYNACL_DIR:=$(BUILD_DIR)/pynacl-$(PYNACL_VERSION)
PYNACL_CAT:=$(ZCAT)

PYNACL_BINARY:=_sodium.so
PYNACL_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/nacl
PYNACL_TARGET_BINARY:=$(PYNACL_SITE_PACKAGE_DIR)/../$(PYNACL_BINARY)

PYNACL_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(PYNACL_SOURCE):
	 $(call DOWNLOAD,$(PYNACL_SITE),$(PYNACL_SOURCE))

$(PYNACL_DIR)/.unpacked: $(DL_DIR)/$(PYNACL_SOURCE)
	$(PYNACL_CAT) $(DL_DIR)/$(PYNACL_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(PYNACL_DIR)/.patched: $(PYNACL_DIR)/.unpacked
	toolchain/patch-kernel.sh $(PYNACL_DIR) package/pynacl/ pynacl-$(PYNACL_VERSION)-\*.patch
	touch $@

# add DISTUTILS_DEBUG=1 to environment to debug setup.py
$(PYNACL_DIR)/.build: $(PYNACL_DIR)/.patched
	pip install cffi # shortcut to install cffi in HOST_DIR
	(cd $(PYNACL_DIR); \
		SODIUM_INSTALL=system \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(PYNACL_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(PYNACL_TARGET_BINARY): $(PYNACL_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(PYNACL_DIR)/dist/PyNaCl-$(PYNACL_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(PYNACL_SITE_PACKAGE_DIR) -name \*.pyc -delete

pynacl: uclibc python cffi $(TARGET_DIR)/$(PYNACL_TARGET_BINARY)

pynacl-unpack: $(PYNACL_DIR)/.unpacked

pynacl-build: $(PYNACL_DIR)/.build

pynacl-install: $(TARGET_DIR)/$(PYNACL_TARGET_BINARY)

pynacl-dirclean:
	rm -rf $(PYNACL_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CFFI),y)
TARGETS+=pynacl
endif
