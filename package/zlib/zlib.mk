#############################################################
#
# zlib
#
#############################################################

ZLIB_VERSION:=1.2.11
ZLIB_SOURCE:=zlib-$(ZLIB_VERSION).tar.xz
ZLIB_CAT:=$(XZCAT)
ZLIB_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/libpng/zlib/$(ZLIB_VERSION)
ZLIB_DIR:=$(BUILD_DIR)/zlib-$(ZLIB_VERSION)

$(DL_DIR)/$(ZLIB_SOURCE):
	$(call DOWNLOAD,$(ZLIB_SITE),$(ZLIB_SOURCE))

$(ZLIB_DIR)/.patched: $(DL_DIR)/$(ZLIB_SOURCE)
	$(ZLIB_CAT) $(DL_DIR)/$(ZLIB_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(ZLIB_DIR) package/zlib/ zlib-$(ZLIB_VERSION)\*.patch
	$(CONFIG_UPDATE) $(@D)
	touch $@

ifneq ($(BR2_PREFER_STATIC_LIB),y)
ZLIB_PIC := -fPIC
ZLIB_SHARED := --shared
ZLIB_TARGET := $(TARGET_DIR)/usr/lib/libz.so
else
ZLIB_PIC :=
ZLIB_SHARED :=
ZLIB_TARGET := $(STAGING_DIR)/usr/lib/libz.a
endif

$(ZLIB_DIR)/.configured: $(ZLIB_DIR)/.patched
	(cd $(ZLIB_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(ZLIB_PIC) $(BR2_PACKAGE_ZLIB_OPTIM)" \
		./configure \
		$(ZLIB_SHARED) \
		--prefix=/usr \
		--eprefix=$(STAGING_DIR)/usr/bin \
		--libdir=$(STAGING_DIR)/usr/lib \
		--includedir=$(STAGING_DIR)/usr/include \
	)
	touch $@

$(ZLIB_DIR)/.built: $(ZLIB_DIR)/.configured
	$(MAKE) -C $(ZLIB_DIR) libz.a
	$(MAKE) -C $(ZLIB_DIR) all
	touch $@

$(STAGING_DIR)/usr/include/zlib.h: $(ZLIB_DIR)/.built
	$(INSTALL) -D $(ZLIB_DIR)/zlib.h $(STAGING_DIR)/usr/include/zlib.h
	$(INSTALL) $(ZLIB_DIR)/zconf.h $(STAGING_DIR)/usr/include/
	touch -c $@

$(STAGING_DIR)/usr/lib/libz.a: $(STAGING_DIR)/usr/include/zlib.h
	$(INSTALL) -D $(ZLIB_DIR)/libz.a $(STAGING_DIR)/usr/lib/libz.a
	touch -c $@

$(STAGING_DIR)/usr/lib/libz.so: $(STAGING_DIR)/usr/include/zlib.h
	cp -dpf $(ZLIB_DIR)/libz.so* $(STAGING_DIR)/usr/lib/
	if ! test -d $(STAGING_DIR)/usr/lib/pkgconfig; then \
		mkdir -p $(STAGING_DIR)/usr/lib/pkgconfig; \
	fi
	cp -dpf $(ZLIB_DIR)/zlib.pc $(STAGING_DIR)/usr/lib/pkgconfig
	touch -c $@

$(TARGET_DIR)/usr/lib/libz.so: $(STAGING_DIR)/usr/lib/libz.so
	mkdir -p $(TARGET_DIR)/usr/lib
	cp -dpf $(STAGING_DIR)/usr/lib/libz.so* $(TARGET_DIR)/usr/lib
	-$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $@
	touch -c $@

$(TARGET_DIR)/usr/lib/libz.a: $(STAGING_DIR)/usr/lib/libz.a
	$(INSTALL) -D $(STAGING_DIR)/usr/include/zlib.h $(TARGET_DIR)/usr/include/zlib.h
	$(INSTALL) $(STAGING_DIR)/usr/include/zconf.h $(TARGET_DIR)/usr/include/
	$(INSTALL) -D $(STAGING_DIR)/usr/lib/libz.a $(TARGET_DIR)/usr/lib/libz.a
	touch -c $@

$(eval $(call AUTOTARGETS_HOST,package,zlib))

$(ZLIB_HOST_CONFIGURE):
	(cd $(ZLIB_HOST_DIR); rm -rf config.cache; \
		./configure \
		--prefix=/usr \
		--eprefix=/usr/bin \
		--libdir=/usr/lib \
		--includedir=/usr/include \
	)
	touch $@

zlib-headers: $(TARGET_DIR)/usr/lib/libz.a

zlib: uclibc $(ZLIB_TARGET)

zlib-source: $(DL_DIR)/$(ZLIB_SOURCE)

zlib-patched: $(ZLIB_DIR)/.patched

zlib-configure:  $(ZLIB_DIR)/.configured

zlib-build: $(ZLIB_DIR)/.built

zlib-clean:
	rm -f $(TARGET_DIR)/usr/lib/libz.* \
	      $(TARGET_DIR)/usr/include/zlib.h \
	      $(TARGET_DIR)/usr/include/zconf.h \
	      $(STAGING_DIR)/usr/include/zlib.h \
	      $(STAGING_DIR)/usr/include/zconf.h \
	      $(STAGING_DIR)/usr/lib/libz.*
	-$(MAKE) -C $(ZLIB_DIR) clean
	rm $(ZLIB_DIR)/.built

zlib-dirclean:
	rm -rf $(ZLIB_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_ZLIB),y)
TARGETS+=zlib
endif
ifeq ($(BR2_PACKAGE_ZLIB_TARGET_HEADERS),y)
TARGETS+=zlib-headers
endif
