#############################################################
#
# gs
#
#############################################################

GS_VERSION = 8.71
GS_SOURCE = ghostscript-$(GS_VERSION).tar.gz
GS_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/ghostscript/GPL%20Ghostscript/$(GS_VERSION)

GS_NAME = gs-$(GS_VERSION)
GS_DIR = $(BUILD_DIR)/$(GS_NAME)

GS_AUTORECONF = YES
GS_LIBTOOL_PATCH = NO
GS_INSTALL_STAGING = YES
GS_INSTALL_TARGET = YES

GS_DEPENDENCIES = uclibc host-autoconf cups tiff jpeg libpng
GS_TARGET_BINARY = /usr/bin/gs

#GS_CONF_OPT = --without-x --disable-cairo --disable-gtk \
#		--disable-fontconfig --with-system-libtiff --with-libiconv=gnu 	
#		--without-jasper --disable-compile-inits

GS_CONF_OPT = --with-system-libtiff --without-jasper
GS_CONF_ENV = CUPSCONFIG=$(STAGING_DIR)/usr/bin/cups-config

$(DL_DIR)/$(GS_SOURCE):
	 $(call DOWNLOAD,$(GS_SITE),$(GS_SOURCE))

$(GS_DIR)/.unpacked: $(DL_DIR)/$(GS_SOURCE)
	mkdir -p $(BUILD_DIR)/$(GS_NAME)
	$(ZCAT) $(DL_DIR)/$(GS_SOURCE) | tar $(TAR_STRIP_COMPONENTS)=1 -C $(BUILD_DIR)/$(GS_NAME) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(GS_DIR) package/gs/ \*.patch
	# I'm not in the mood to make a patch
	$(SED) 's|INCLUDE=/usr/include|INCLUDE=$(STAGING_DIR)/usr/include|' $(GS_DIR)/base/unix-aux.mak
	cp $(GS_DIR)/base/unix-aux.mak $(GS_DIR)/base/unix-aux.mak-safe
	cp package/gs/cups.mak $(GS_DIR)/cups/ # prevents rebuilding mkromfs
	$(CONFIG_UPDATE) $(GS_DIR)
	touch $@

$(GS_DIR)/.configured: $(GS_DIR)/.unpacked
	cd $(GS_DIR) && $(AUTOCONF)
	(cd $(GS_DIR) && \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(GS_CONF_ENV) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--libdir=/usr/lib \
		--sysconfdir=/etc \
		--localstatedir=/var \
		$(GS_CONF_OPT) \
		)
	touch $@

# host tools must be compiled with native CC, and generate a arch.h
$(GS_DIR)/.hosttools: $(GS_DIR)/.configured
	(cd $(GS_DIR); \
		mkdir -p obj; \
		rm -f obj/arch.h; \
		cp $(GS_DIR)/base/unix-aux.mak-safe $(GS_DIR)/base/unix-aux.mak; \
		for i in genarch genconf mkromfs echogs gendev genht; do \
			rm -f obj/$$i; \
			$(MAKE1) CC=$(HOSTCC) CCAUX="$(HOSTCC)" EXTRALIBS="" obj/$$i; \
		done; \
		rm -f obj/*.o; \
	)
	touch $@

# use a arch.h generated in the target by running "genarch" there
# prevents mkromfs to be re-compiled
$(GS_DIR)/.compiled: $(GS_DIR)/.hosttools
	cp package/gs/dns323-arch.h $(GS_DIR)/obj/arch.h
	cp package/gs/unix-aux.mak $(GS_DIR)/base/
	$(SED) 's|INCLUDE=/usr/include|INCLUDE=$(STAGING_DIR)/usr/include|' $(GS_DIR)/base/unix-aux.mak
	$(MAKE1) -C $(GS_DIR)
	touch $@

$(TARGET_DIR)/$(GS_TARGET_BINARY): $(GS_DIR)/.compiled
	$(MAKE1) -C $(GS_DIR) DESTDIR=$(TARGET_DIR) install
	rm -rf $(TARGET_DIR)/usr/share/ghostscript/8.71/examples $(TARGET_DIR)/usr/share/ghostscript/8.71/doc
	touch $@

gs: $(GS_DEPENDENCIES) $(TARGET_DIR)/$(GS_TARGET_BINARY)

gs-install: $(TARGET_DIR)/$(GS_TARGET_BINARY)

gs-build: $(GS_DIR)/.compiled

gs-hosttools: $(GS_DIR)/.hosttools

gs-configure: $(GS_DIR)/.configured

gs-extract: $(GS_DIR)/.unpacked

gs-source: $(DL_DIR)/$(GS_SOURCE)

gs-clean:
	-$(MAKE) -C $(GS_DIR) clean

gs-dirclean:
	rm -fr $(GS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_GS),y)
TARGETS+=gs
endif
