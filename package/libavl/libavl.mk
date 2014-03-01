#############################################################
#
# libavl
#
#############################################################

LIBAVL_VERSION:=0.3.5
LIBAVL_SITE:=$(BR2_DEBIAN_MIRROR)/debian/pool/main/liba/libavl
LIBAVL_SOURCE=libavl_$(LIBAVL_VERSION).orig.tar.gz

LIBAVL_LIBTOOL_PATCH = NO
LIBAVL_INSTALL_STAGING = YES

LIBAVL_DIR=$(BUILD_DIR)/libavl-$(LIBAVL_VERSION)
LIBAVL_DESTDIR:=usr/lib

LIBAVL_TARGET=libavl.so.1.5
LIBAVL_TARGET_LIBRARY=$(LIBAVL_DESTDIR)/$(LIBAVL_TARGET)

$(DL_DIR)/$(LIBAVL_SOURCE):
	$(call DOWNLOAD,$(LIBAVL_SITE),$(LIBAVL_SOURCE))

$(LIBAVL_DIR)/.source: $(DL_DIR)/$(LIBAVL_SOURCE)
	mkdir -p $(LIBAVL_DIR)
	$(ZCAT) $(DL_DIR)/$(LIBAVL_SOURCE) | tar $(TAR_STRIP_COMPONENTS)=1 -C $(LIBAVL_DIR)/ $(TAR_OPTIONS) -
	touch $@

$(LIBAVL_DIR)/.configured: $(LIBAVL_DIR)/.source
	touch $@

$(LIBAVL_DIR)/$(LIBAVL_TARGET): $(LIBAVL_DIR)/.configured
	$(MAKE) -C $(LIBAVL_DIR) CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)"
	touch $@

$(TARGET_DIR)/$(LIBAVL_TARGET_LIBRARY): $(LIBAVL_DIR)/$(LIBAVL_TARGET)
	cp $(LIBAVL_DIR)/$(LIBAVL_TARGET) $(TARGET_DIR)/$(LIBAVL_DESTDIR)
	cp $(LIBAVL_DIR)/$(LIBAVL_TARGET) $(STAGING_DIR)/$(LIBAVL_DESTDIR)
	ln -sf $(STAGING_DIR)/$(LIBAVL_TARGET_LIBRARY) $(STAGING_DIR)/$(LIBAVL_DESTDIR)/libavl.so
	cp $(LIBAVL_DIR)/avl.h $(STAGING_DIR)/usr/include

libavl-build: $(LIBAVL_DIR)/$(LIBAVL_TARGET)

libavl-configure: $(LIBAVL_DIR)/.configured

libavl: $(TARGET_DIR)/$(LIBAVL_TARGET_LIBRARY)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_LIBAVL),y)
TARGETS+=libavl
endif
