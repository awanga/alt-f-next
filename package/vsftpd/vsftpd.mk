#############################################################
#
# vsftpd
#
#############################################################

VSFTPD_VERSION:=3.0.3
VSFTPD_SOURCE:=vsftpd-$(VSFTPD_VERSION).tar.gz
VSFTPD_SITE:=https://security.appspot.com/downloads
VSFTPD_DIR:=$(BUILD_DIR)/vsftpd-$(VSFTPD_VERSION)
VSFTPD_CAT:=$(ZCAT)
VSFTPD_BINARY:=vsftpd
VSFTPD_TARGET_BINARY:=usr/sbin/vsftpd

ifeq ($(BR2_PACKAGE_OPENSSL),y)
VSFTPD_LIBS:=-lcrypto -lcrypt -lssl
else
VSFTPD_LIBS:=-lcrypt
endif

$(DL_DIR)/$(VSFTPD_SOURCE):
	 $(call DOWNLOAD,$(VSFTPD_SITE),$(VSFTPD_SOURCE))

vsftpd-source: $(DL_DIR)/$(VSFTPD_SOURCE)

$(VSFTPD_DIR)/.unpacked: $(DL_DIR)/$(VSFTPD_SOURCE)
	$(VSFTPD_CAT) $(DL_DIR)/$(VSFTPD_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(VSFTPD_DIR) package/vsftpd/ vsftpd-$(VSFTPD_VERSION)\*.patch
	touch $@

$(VSFTPD_DIR)/.configured: $(VSFTPD_DIR)/.unpacked
ifeq ($(BR2_PACKAGE_OPENSSL),y)
	$(SED) 's,#undef[[:space:]]*VSF_BUILD_SSL.*,#define VSF_BUILD_SSL,g' $(VSFTPD_DIR)/builddefs.h
else
	$(SED) 's,#define[[:space:]]*VSF_BUILD_SSL.*,#undef VSF_BUILD_SSL,g' $(VSFTPD_DIR)/builddefs.h
endif
ifneq ($(findstring uclibc,$(BR2_GNU_TARGET_SUFFIX)),)
	$(SED) 's,#define[[:space:]]*VSF_BUILDDEFS_H.*,#define VSF_BUILDDEFS_H\n#define __UCLIBC__,g' $(VSFTPD_DIR)/builddefs.h
	$(SED) 's,.*__UCLIBC_HAS_LFS__.*,,g' $(VSFTPD_DIR)/builddefs.h
ifeq ($(BR2_LARGEFILE),y)
	$(SED) 's,#define[[:space:]]*VSF_BUILDDEFS_H.*,#define VSF_BUILDDEFS_H\n#define __UCLIBC_HAS_LFS__,g' $(VSFTPD_DIR)/builddefs.h
endif
else # not uclibc
	$(SED) 's,.*__UCLIBC_.*,,g' $(VSFTPD_DIR)/builddefs.h
endif
	touch $@

$(VSFTPD_DIR)/.built: $(VSFTPD_DIR)/.configured
	$(MAKE) CC=$(TARGET_CC) CFLAGS="$(TARGET_CFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" LIBS="$(VSFTPD_LIBS)" -C $(VSFTPD_DIR)
	touch $@

$(TARGET_DIR)/$(VSFTPD_TARGET_BINARY): $(VSFTPD_DIR)/.built
	cp -dpf $(VSFTPD_DIR)/$(VSFTPD_BINARY) $@
	$(INSTALL) -D -m 0755 package/vsftpd/vsftpd-init $(TARGET_DIR)/etc/init.d/S70vsftpd

ifeq ($(BR2_PACKAGE_OPENSSL),y)
vsftpd: uclibc openssl $(TARGET_DIR)/$(VSFTPD_TARGET_BINARY)
else
vsftpd: uclibc $(TARGET_DIR)/$(VSFTPD_TARGET_BINARY)
endif

vsftpd-patch: $(VSFTPD_DIR)/.unpacked

vsftpd-configure: $(VSFTPD_DIR)/.configured

vsftpd-build: $(VSFTPD_DIR)/.built

vsftpd-clean:
	-$(MAKE) -C $(VSFTPD_DIR) clean
	rm -f $(TARGET_DIR)/$(VSFTPD_TARGET_BINARY) $(VSFTPD_DIR)/.built

vsftpd-dirclean:
	rm -rf $(VSFTPD_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_VSFTPD),y)
TARGETS+=vsftpd
endif
