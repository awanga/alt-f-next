#############################################################
#
# mdadm
#
#############################################################

# 3.1.5 incremental NOT OK
MDADM_VERSION:=3.1.5
# 3.2.6 incremental OK, +63KB then 3.1.5
#MDADM_VERSION:=3.2.6
# 3.3.2 incremental OK, + 54KB than 3.2.6
#MDADM_VERSION:=3.3.2

MDADM_SOURCE:=mdadm-$(MDADM_VERSION).tar.gz
MDADM_CAT:=$(ZCAT)
MDADM_SITE:=http://www.kernel.org/pub/linux/utils/raid/mdadm/
MDADM_DIR:=$(BUILD_DIR)/mdadm-$(MDADM_VERSION)
MDADM_BINARY:=mdadm
MDADM_TARGET_BINARY:=sbin/mdadm
MDADM_CFLAGS=-Os

$(DL_DIR)/$(MDADM_SOURCE): $(MDADM_PATCH_FILE)
	$(call DOWNLOAD,$(MDADM_SITE),$(MDADM_SOURCE))
	touch -c $@

$(MDADM_DIR)/.unpacked: $(DL_DIR)/$(MDADM_SOURCE)
	$(MDADM_CAT) $(DL_DIR)/$(MDADM_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(MDADM_DIR) package/mdadm mdadm-$(MDADM_VERSION)\*.patch
	touch $@

$(MDADM_DIR)/.built: $(MDADM_DIR)/.unpacked
	$(MAKE) CFLAGS="$(TARGET_CFLAGS) $(MDADM_CFLAGS) -DUCLIBC -DHAVE_STDINT_H" CC=$(TARGET_CC) -C $(MDADM_DIR)
	touch $@

$(TARGET_DIR)/$(MDADM_TARGET_BINARY): $(MDADM_DIR)/.built
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(MDADM_DIR) install
	rm -Rf $(TARGET_DIR)/usr/share/man
	$(STRIPCMD) $(STRIP_STRIP_ALL) $@

mdadm-build: $(MDADM_DIR)/.built

mdadm-source: $(DL_DIR)/$(MDADM_SOURCE) $(MDADM_PATCH_FILE)

mdadm-unpacked: $(MDADM_DIR)/.unpacked

mdadm: uclibc $(TARGET_DIR)/$(MDADM_TARGET_BINARY)

mdadm-clean:
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(MDADM_DIR) uninstall
	-$(MAKE) -C $(MDADM_DIR) clean

mdadm-dirclean:
	rm -rf $(MDADM_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_MDADM),y)
TARGETS+=mdadm
endif
