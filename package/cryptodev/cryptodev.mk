#############################################################
#
# cryptodev
#
#############################################################

CRYPTODEV_VERSION:=1.7
CRYPTODEV_SOURCE:=cryptodev-linux-$(CRYPTODEV_VERSION).tar.gz
CRYPTODEV_SITE:=http://download.gna.org/cryptodev-linux
CRYPTODEV_DIR:=$(BUILD_DIR)/cryptodev-$(CRYPTODEV_VERSION)
CRYPTODEV_MOD:=cryptodev.ko
CRYPTODEV_TARGET_MOD:=cryptodev/cryptodev.ko

CRYPTODEV_DEPENDENCIES = uclibc $(STAGING_DIR)/usr/include/crypto/cryptodev.h

ifneq ($(BR2_PACKAGE_CRYPTODEV_HEADER_ONLY),y)
	CRYPTODEV_DEPENDENCIES += linux26-modules  $(TARGET_DIR)/lib/modules/$(LINVER)/$(CRYPTODEV_TARGET_MOD)
endif

$(DL_DIR)/$(CRYPTODEV_SOURCE):
	$(call DOWNLOAD,$(CRYPTODEV_SITE),$(CRYPTODEV_SOURCE))

$(CRYPTODEV_DIR)/.source: $(DL_DIR)/$(CRYPTODEV_SOURCE)
	mkdir -p $(CRYPTODEV_DIR)
	$(ZCAT) $(DL_DIR)/$(CRYPTODEV_SOURCE) | tar --strip-components=1 -C $(CRYPTODEV_DIR) $(TAR_OPTIONS) -
	touch $@

$(STAGING_DIR)/usr/include/crypto/cryptodev.h: $(CRYPTODEV_DIR)/.source
	mkdir -p $(STAGING_DIR)/usr/include/crypto
	cp $(CRYPTODEV_DIR)/crypto/cryptodev.h $(STAGING_DIR)/usr/include/crypto

$(CRYPTODEV_DIR)/$(CRYPTODEV_MOD): $(CRYPTODEV_DIR)/.source $(PROJECT_BUILD_DIR)/autotools-stamps/kernel-modules_target_installed
	$(LINUX26_MAKE_FLAGS) $(MAKE) KERNEL_DIR=$(LINUX_DIR) -C $(CRYPTODEV_DIR) build

# for some reason, LINUX26_VERSION, defined in target/linux/Makefile.in
# is not defined here for the target and dependencies (but it is for the recipe!),
# so other variable has to be used. But quotes has to be removed from it.
quote:="
LINVER=$(subst $(quote),$(empty),$(BR2_LINUX26_VERSION))

$(TARGET_DIR)/lib/modules/$(LINVER)/$(CRYPTODEV_TARGET_MOD): $(CRYPTODEV_DIR)/$(CRYPTODEV_MOD)
	mkdir -p $(TARGET_DIR)/lib/modules/$(LINVER)/cryptodev
	cp $(CRYPTODEV_DIR)/$(CRYPTODEV_MOD) $(TARGET_DIR)/lib/modules/$(LINVER)/$(CRYPTODEV_TARGET_MOD)
	$(STAGING_DIR)/bin/$(GNU_TARGET_NAME)-depmod26 -b $(TARGET_DIR) $(LINVER)

cryptodev: $(CRYPTODEV_DEPENDENCIES)

cryptodev-build: $(CRYPTODEV_DIR)/$(CRYPTODEV_MOD)

cryptodev-extract: $(CRYPTODEV_DIR)/.source

cryptodev-source: $(DL_DIR)/$(CRYPTODEV_SOURCE)

cryptodev-dirclean:
	rm -rf $(CRYPTODEV_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CRYPTODEV),y)
TARGETS+=cryptodev
endif
 
