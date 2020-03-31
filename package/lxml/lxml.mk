#############################################################
#
# lxml
#
############################################################

# stop natively compiling on host after this version (are libxml2 or libxslt too old?)
#LXML_VERSION = 4.1.1
LXML_VERSION = 4.4.1

LXML_SOURCE = lxml-$(LXML_VERSION).tgz
LXML_SITE = http://lxml.de/files/

LXML_AUTORECONF = NO
LXML_INSTALL_STAGING = NO
LXML_INSTALL_TARGET = YES
LXML_LIBTOOL_PATCH = NO

LXML_DIR:=$(BUILD_DIR)/lxml-$(LXML_VERSION)
LXML_CAT:=$(ZCAT)

LXML_BINARY:=etree.so
LXML_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/lxml
LXML_TARGET_BINARY=$(LXML_SITE_PACKAGE_DIR)/$(LXML_BINARY)

LXML_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(LXML_SOURCE):
	 $(call DOWNLOAD,$(LXML_SITE),$(LXML_SOURCE))
	mkdir -p $(BUILD_DIR)/lxml-$(LXML_VERSION)	

$(LXML_DIR)/.unpacked: $(DL_DIR)/$(LXML_SOURCE)
	$(LXML_CAT) $(DL_DIR)/$(LXML_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(LXML_DIR)/.patched: $(LXML_DIR)/.unpacked
	toolchain/patch-kernel.sh $(LXML_DIR) package/lxml/ lxml-$(LXML_VERSION)-\*.patch
	touch $@

$(LXML_DIR)/.build: $(LXML_DIR)/.patched
	(cd $(LXML_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(LXML_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(LXML_TARGET_BINARY): $(LXML_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(LXML_DIR)/dist/lxml-$(LXML_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(LXML_SITE_PACKAGE_DIR) -name \*.pyc -delete
	touch $(TARGET_DIR)/$(LXML_TARGET_BINARY)

lxml: libxml2 libxslt zlib python $(TARGET_DIR)/$(LXML_TARGET_BINARY)

lxml-unpack: $(LXML_DIR)/.unpacked

lxml-build: libxml2 libxslt zlib python $(LXML_DIR)/.build

lxml-install: libxml2 libxslt zlib python $(TARGET_DIR)/$(LXML_TARGET_BINARY)

lxml-dirclean:
	rm -rf $(LXML_DIR)

#############################################################
#
# Toplevel Makefile options
#
############################################################
ifeq ($(BR2_PACKAGE_LXML),y)
TARGETS+=lxml
endif
