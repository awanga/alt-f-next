#############################################################
#
# cheetah
#
#############################################################

CHEETAH_VERSION=2.4.4
CHEETAH_SOURCE:=Cheetah-$(CHEETAH_VERSION).tar.gz
CHEETAH_SITE:=http://pypi.python.org/packages/source/C/Cheetah

CHEETAH_DIR:=$(BUILD_DIR)/Cheetah-$(CHEETAH_VERSION)
CHEETAH_CAT:=$(ZCAT)

CHEETAH_BINARY:=_namemapper.so
CHEETAH_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/Cheetah
CHEETAH_TARGET_BINARY:=$(CHEETAH_SITE_PACKAGE_DIR)/$(CHEETAH_BINARY)

CHEETAH_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(CHEETAH_SOURCE):
	 $(call DOWNLOAD,$(CHEETAH_SITE),$(CHEETAH_SOURCE))

$(CHEETAH_DIR)/.unpacked: $(DL_DIR)/$(CHEETAH_SOURCE)
	$(CHEETAH_CAT) $(DL_DIR)/$(CHEETAH_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(CHEETAH_DIR)/.patched: $(CHEETAH_DIR)/.unpacked
	toolchain/patch-kernel.sh $(CHEETAH_DIR) package/cheetah/ cheetah-$(CHEETAH_VERSION)-\*.patch
	touch $@

$(CHEETAH_DIR)/.build: $(CHEETAH_DIR)/.patched
	(cd $(CHEETAH_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(CHEETAH_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(CHEETAH_TARGET_BINARY): $(CHEETAH_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(CHEETAH_DIR)/dist/Cheetah-$(CHEETAH_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(CHEETAH_SITE_PACKAGE_DIR) -name \*.pyc -delete

cheetah: uclibc python $(TARGET_DIR)/$(CHEETAH_TARGET_BINARY)

cheetah-build: $(CHEETAH_DIR)/.build

cheetah-install: $(TARGET_DIR)/$(CHEETAH_TARGET_BINARY)

cheetah-dirclean:
	rm -rf $(CHEETAH_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CHEETAH),y)
TARGETS+=cheetah
endif
