#############################################################
#
# make
#
#############################################################
MAKE_VERSION:=3.81
MAKE_SOURCE:=make-$(MAKE_VERSION).tar.bz2
MAKE_SITE:=$(BR2_GNU_MIRROR)/make
MAKE_DIR:=$(BUILD_DIR)/make-$(MAKE_VERSION)
MAKE_CAT:=$(BZCAT)
MAKE_BINARY:=make
MAKE_TARGET_BINARY:=usr/bin/make

$(DL_DIR)/$(MAKE_SOURCE):
	 $(call DOWNLOAD,$(MAKE_SITE),$(MAKE_SOURCE))

make-source: $(DL_DIR)/$(MAKE_SOURCE)

$(MAKE_DIR)/.unpacked: $(DL_DIR)/$(MAKE_SOURCE)
	$(MAKE_CAT) $(DL_DIR)/$(MAKE_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	$(CONFIG_UPDATE) $(MAKE_DIR)/config
	touch $@

$(MAKE_DIR)/.configured: $(MAKE_DIR)/.unpacked
	(cd $(MAKE_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		make_cv_sys_gnu_glob=no \
		GLOBINC='-I$(MAKE_DIR)/glob' \
		GLOBLIB=glob/libglob.a \
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
	touch $@

$(MAKE_DIR)/$(MAKE_BINARY): $(MAKE_DIR)/.configured
	$(MAKE) MAKE=$(HOSTMAKE) -C $(MAKE_DIR)

$(TARGET_DIR)/$(MAKE_TARGET_BINARY): $(MAKE_DIR)/$(MAKE_BINARY)
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(MAKE_DIR) install
	rm -rf $(TARGET_DIR)/share/locale $(TARGET_DIR)/usr/info \
		$(TARGET_DIR)/usr/man $(TARGET_DIR)/usr/share/doc

make: uclibc $(if $(BR2_PACKAGE_GETTEXT),gettext) $(TARGET_DIR)/$(MAKE_TARGET_BINARY)

make-clean:
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(MAKE_DIR) uninstall
	-$(MAKE) -C $(MAKE_DIR) clean

make-dirclean:
	rm -rf $(MAKE_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_MAKE),y)
TARGETS+=make
endif
