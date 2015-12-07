#############################################################
#
# smartmontools
#
#############################################################

SMARTMONTOOLS_VERSION:=6.4
SMARTMONTOOLS_SOURCE:=smartmontools-$(SMARTMONTOOLS_VERSION).tar.gz
SMARTMONTOOLS_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/smartmontools/smartmontools/$(SMARTMONTOOLS_VERSION)

SMARTMONTOOLS_DIR:=$(BUILD_DIR)/smartmontools-$(SMARTMONTOOLS_VERSION)
SMARTMONTOOLS_CAT:=$(ZCAT)
SMARTMONTOOLS_BINARY:=smartctl
SMARTMONTOOLS_BINARY2:=smartd
SMARTMONTOOLS_TARGET_BINARY:=usr/sbin/smartctl
SMARTMONTOOLS_TARGET_BINARY2:=usr/sbin/smartd

SMARTMONTOOLS_CFLAGS=-Os

$(DL_DIR)/$(SMARTMONTOOLS_SOURCE):
	 $(call DOWNLOAD,$(SMARTMONTOOLS_SITE),$(SMARTMONTOOLS_SOURCE))

smartmontools-source: $(DL_DIR)/$(SMARTMONTOOLS_SOURCE)

$(SMARTMONTOOLS_DIR)/.unpacked: $(DL_DIR)/$(SMARTMONTOOLS_SOURCE)
	$(SMARTMONTOOLS_CAT) $(DL_DIR)/$(SMARTMONTOOLS_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(SMARTMONTOOLS_DIR) package/smartmontools/ \*.patch
	touch $(SMARTMONTOOLS_DIR)/.unpacked

$(SMARTMONTOOLS_DIR)/.configured: $(SMARTMONTOOLS_DIR)/.unpacked
	(cd $(SMARTMONTOOLS_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		CFLAGS="$(TARGET_CFLAGS) $(SMARTMONTOOLS_CFLAGS)" \
		CXXFLAGS="$(TARGET_CFLAGS) $(SMARTMONTOOLS_CFLAGS)" \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--bindir=/usr/bin \
		--sbindir=/usr/sbin \
		--libdir=/lib \
		--libexecdir=/usr/lib \
		--sysconfdir=/etc \
		--datadir=/usr/share \
		--localstatedir=/var \
		--mandir=/usr/man \
		--infodir=/usr/info \
		$(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
	)
	touch $(SMARTMONTOOLS_DIR)/.configured

$(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY): $(SMARTMONTOOLS_DIR)/.configured
	$(MAKE) -C $(SMARTMONTOOLS_DIR)
	$(STRIPCMD) $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY)
	$(STRIPCMD) $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY2)
	touch -c $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY)

$(TARGET_DIR)/$(SMARTMONTOOLS_TARGET_BINARY): $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY)
	mkdir -p $(TARGET_DIR)/usr/sbin
	cp $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY) $(TARGET_DIR)/usr/sbin/
	cp $(SMARTMONTOOLS_DIR)/smartd_warning.sh $(TARGET_DIR)/etc/

$(TARGET_DIR)/$(SMARTMONTOOLS_TARGET_BINARY2): $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY2)
	mkdir -p $(TARGET_DIR)/usr/sbin
	cp $(SMARTMONTOOLS_DIR)/$(SMARTMONTOOLS_BINARY2) $(TARGET_DIR)/usr/sbin/
	cp $(SMARTMONTOOLS_DIR)/smartd_warning.sh $(TARGET_DIR)/etc/

smartmontools: uclibc $(TARGET_DIR)/$(SMARTMONTOOLS_TARGET_BINARY) $(TARGET_DIR)/$(SMARTMONTOOLS_TARGET_BINARY2)

smartmontools-configure: $(SMARTMONTOOLS_DIR)/.configured

smartmontools-patch: $(SMARTMONTOOLS_DIR)/.unpacked

smartmontools-clean:
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(SMARTMONTOOLS_DIR) uninstall
	-$(MAKE) -C $(SMARTMONTOOLS_DIR) clean

smartmontools-dirclean:
	rm -rf $(SMARTMONTOOLS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_SMARTMONTOOLS),y)
TARGETS+=smartmontools
endif
