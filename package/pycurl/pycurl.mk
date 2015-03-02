#############################################################
#
# pycurl
#
#############################################################

PYCURL_VERSION = 7.19.5
PYCURL_SOURCE = pycurl-$(PYCURL_VERSION).tar.gz
PYCURL_SITE = http://pycurl.sourceforge.net/download

PYCURL_AUTORECONF = NO
PYCURL_INSTALL_STAGING = NO
PYCURL_INSTALL_TARGET = NO
PYCURL_LIBTOOL_PATCH = NO

PYCURL_DIR:=$(BUILD_DIR)/pycurl-$(PYCURL_VERSION)
PYCURL_CAT:=$(ZCAT)

PYCURL_BINARY:=pycurl.so
PYCURL_SITE_PACKAGE_DIR=usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages/curl
PYCURL_TARGET_BINARY:=$(PYCURL_SITE_PACKAGE_DIR)/../$(PYCURL_BINARY)

PYCURL_CFLAGS = CFLAGS+=" -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)"

$(DL_DIR)/$(PYCURL_SOURCE):
	 $(call DOWNLOAD,$(PYCURL_SITE),$(PYCURL_SOURCE))

$(PYCURL_DIR)/.unpacked: $(DL_DIR)/$(PYCURL_SOURCE)
	$(PYCURL_CAT) $(DL_DIR)/$(PYCURL_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(PYCURL_DIR)/.patched: $(PYCURL_DIR)/.unpacked
	toolchain/patch-kernel.sh $(PYCURL_DIR) package/pycurl/ pycurl-$(PYCURL_VERSION)-\*.patch
	touch $@

$(PYCURL_DIR)/.build: $(PYCURL_DIR)/.patched
	(cd $(PYCURL_DIR); \
		$(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV) LDSHARED="$(TARGET_CC) -shared" $(PYCURL_CFLAGS) \
		LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python setup.py \
		bdist_dumb --plat-name $(GNU_TARGET_NAME) --relative \
	)
	touch $@

$(TARGET_DIR)/$(PYCURL_TARGET_BINARY): $(PYCURL_DIR)/.build
	tar -C $(TARGET_DIR)/usr -xf $(PYCURL_DIR)/dist/pycurl-$(PYCURL_VERSION).$(GNU_TARGET_NAME).tar.gz
	find $(TARGET_DIR)/$(PYCURL_SITE_PACKAGE_DIR) -name \*.pyc -delete

pycurl: uclibc libcurl python $(TARGET_DIR)/$(PYCURL_TARGET_BINARY)

pycurl-unpack: $(PYCURL_DIR)/.unpacked

pycurl-build: $(PYCURL_DIR)/.build

pycurl-install: $(TARGET_DIR)/$(PYCURL_TARGET_BINARY)

pycurl-dirclean:
	rm -rf $(PYCURL_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_PYCURL),y)
TARGETS+=pycurl
endif
