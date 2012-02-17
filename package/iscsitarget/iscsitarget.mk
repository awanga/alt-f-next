#############################################################
#
# iscsitarget
#
#############################################################

ISCSITARGET_VERSION:=1.4.20.2
ISCSITARGET_SOURCE:=iscsitarget-$(ISCSITARGET_VERSION).tar.gz
ISCSITARGET_SITE:=http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/iscsitarget
ISCSITARGET_DIR:=$(BUILD_DIR)/iscsitarget-$(ISCSITARGET_VERSION)
ISCSITARGET_BIN:=usr/ietd
ISCSITARGET_MOD:=kernel/iscsi_trgt.ko
ISCSITARGET_TARGET_BIN:=usr/sbin/ietd
ISCSITARGET_TARGET_MOD:=iscsi/iscsi_trgt.ko

$(DL_DIR)/$(ISCSITARGET_SOURCE):
	$(call DOWNLOAD,$(ISCSITARGET_SITE),$(ISCSITARGET_SOURCE))

$(ISCSITARGET_DIR)/.source: $(DL_DIR)/$(ISCSITARGET_SOURCE)
	$(ZCAT) $(DL_DIR)/$(ISCSITARGET_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(ISCSITARGET_DIR)/$(ISCSITARGET_BIN): $(ISCSITARGET_DIR)/.source
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(ISCSITARGET_DIR) usr

$(ISCSITARGET_DIR)/$(ISCSITARGET_MOD): $(ISCSITARGET_DIR)/.source $(PROJECT_BUILD_DIR)/autotools-stamps/linux_modules_target_installed
	KSRC=$(LINUX_DIR) $(MAKE) -C $(ISCSITARGET_DIR) clean
	$(LINUX26_MAKE_FLAGS) KSRC=$(LINUX_DIR) $(MAKE) -C $(ISCSITARGET_DIR) kernel

$(TARGET_DIR)/$(ISCSITARGET_TARGET_BIN): $(ISCSITARGET_DIR)/$(ISCSITARGET_BIN) 
	cp $(ISCSITARGET_DIR)/usr/{ietd,ietadm} $(TARGET_DIR)/usr/sbin
	mkdir -p $(TARGET_DIR)/etc/iet
	cp $(ISCSITARGET_DIR)/etc/{ietd.conf,initiators.allow,targets.allow} $(TARGET_DIR)/etc/iet/

# for some reason, LINUX26_VERSION, defined in target/linux/Makefile.in
# is not defined here for the target and dependencies (but it is for the recipe!),
# so other variable has to be used. But quotes has to be removed from it.
quote:="
LINVER=$(subst $(quote),$(empty),$(BR2_LINUX26_VERSION))

$(TARGET_DIR)/lib/modules/$(LINVER)/$(ISCSITARGET_TARGET_MOD): $(ISCSITARGET_DIR)/$(ISCSITARGET_MOD)
	mkdir -p $(TARGET_DIR)/lib/modules/$(LINVER)/iscsi
	cp $(ISCSITARGET_DIR)/kernel/iscsi_trgt.ko $(TARGET_DIR)/lib/modules/$(LINVER)/$(ISCSITARGET_TARGET_MOD)
	$(STAGING_DIR)/bin/$(GNU_TARGET_NAME)-depmod26 -b $(TARGET_DIR) $(LINVER)

iscsitarget: uclibc linux26-modules $(TARGET_DIR)/lib/modules/$(LINVER)/$(ISCSITARGET_TARGET_MOD) $(TARGET_DIR)/$(ISCSITARGET_TARGET_BIN)

iscsitarget-build: $(ISCSITARGET_DIR)/$(ISCSITARGET_TARGET)

iscsitarget-extract: $(ISCSITARGET_DIR)/.source

iscsitarget-source: $(DL_DIR)/$(ISCSITARGET_SOURCE)

iscsitarget-dirclean:
	rm -rf $(ISCSITARGET_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_ISCSITARGET),y)
TARGETS+=iscsitarget
endif
 
