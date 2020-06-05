#############################################################
#
# libgpg-error
#
#############################################################

#LIBGPG_ERROR_VERSION:=1.6
LIBGPG_ERROR_VERSION:=1.10
LIBGPG_ERROR_SOURCE:=libgpg-error-$(LIBGPG_ERROR_VERSION).tar.bz2
LIBGPG_ERROR_SITE:=http://www.gnupg.org/ftp/gcrypt/libgpg-error
LIBGPG_ERROR_DIR:=$(BUILD_DIR)/libgpg-error-$(LIBGPG_ERROR_VERSION)
LIBGPG_ERROR_LIBRARY:=src/libgpg-error.la
LIBGPG_ERROR_DESTDIR:=usr/lib
LIBGPG_ERROR_TARGET_LIBRARY=$(LIBGPG_ERROR_DESTDIR)/libgpg-error.so

$(DL_DIR)/$(LIBGPG_ERROR_SOURCE):
	$(call DOWNLOAD,$(LIBGPG_ERROR_SITE),$(LIBGPG_ERROR_SOURCE))

$(LIBGPG_ERROR_DIR)/.source: $(DL_DIR)/$(LIBGPG_ERROR_SOURCE)
	$(BZCAT) $(DL_DIR)/$(LIBGPG_ERROR_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(LIBGPG_ERROR_DIR) package/libgpg-error/ libgpg-error\*.patch
	$(CONFIG_UPDATE) $(LIBGPG_ERROR_DIR)
	touch $@

$(LIBGPG_ERROR_DIR)/.configured: $(LIBGPG_ERROR_DIR)/.source
	(cd $(LIBGPG_ERROR_DIR); rm -f config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--bindir=/usr/bin \
		--sbindir=/usr/sbin \
		--libdir=/usr/lib \
		--libexecdir=/$(LIBGPG_ERROR_DESTDIR) \
		--sysconfdir=/etc \
		--datadir=/usr/share \
		--localstatedir=/var \
		--includedir=/usr/include \
		--mandir=/usr/man \
		--infodir=/usr/info \
		$(DISABLE_NLS) \
	)
	touch $@

$(LIBGPG_ERROR_DIR)/$(LIBGPG_ERROR_LIBRARY): $(LIBGPG_ERROR_DIR)/.configured
	$(MAKE) CC=$(TARGET_CC) -C $(LIBGPG_ERROR_DIR)

$(STAGING_DIR)/$(LIBGPG_ERROR_TARGET_LIBRARY): $(LIBGPG_ERROR_DIR)/$(LIBGPG_ERROR_LIBRARY)
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(LIBGPG_ERROR_DIR) install
	$(SED) "s,^libdir=.*,libdir=\'$(STAGING_DIR)/usr/lib\',g" $(STAGING_DIR)/usr/lib/libgpg-error.la	
	sed -i 's|includedir=\(.*\)|includedir='$(STAGING_DIR)'\1|' $(STAGING_DIR)/usr/bin/gpg-error-config
	sed -i 's|libdir=\(.*\)|libdir='$(STAGING_DIR)'\1|' $(STAGING_DIR)/usr/bin/gpg-error-config

$(TARGET_DIR)/$(LIBGPG_ERROR_TARGET_LIBRARY): $(STAGING_DIR)/$(LIBGPG_ERROR_TARGET_LIBRARY)
	cp -dpf $<* $(TARGET_DIR)/$(LIBGPG_ERROR_DESTDIR)

libgpg-error: uclibc $(TARGET_DIR)/$(LIBGPG_ERROR_TARGET_LIBRARY)

libgpg-error-build: $(LIBGPG_ERROR_DIR)/$(LIBGPG_ERROR_LIBRARY)

libgpg-error-configure: $(LIBGPG_ERROR_DIR)/.configured

libgpg-error-source: $(DL_DIR)/$(LIBGPG_ERROR_SOURCE)

libgpg-error-clean:
	rm -f $(TARGET_DIR)/$(LIBGPG_ERROR_TARGET_LIBRARY)*
	-$(MAKE) -C $(LIBGPG_ERROR_DIR) clean
	rm -f $(STAGING_DIR)/$(LIBGPG_ERROR_TARGET_LIBRARY)\*

libgpg-error-dirclean:
	rm -rf $(LIBGPG_ERROR_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_LIBGPG_ERROR),y)
TARGETS+=libgpg-error
endif
