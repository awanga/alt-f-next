PROJECT_FILE:=$(LOCAL)/$(PROJECT)/$(PROJECT).config


.PHONY: target-host-info saveconfig getconfig

target-host-info: $(TARGET_DIR)/etc/issue $(TARGET_DIR)/etc/hostname $(TARGET_DIR)/etc/br-version

$(TARGET_DIR)/etc/issue: .config
	mkdir -p $(TARGET_DIR)/etc
	echo "" > $@
	echo "" >> $@
	echo "$(BANNER)" >> $@

$(TARGET_DIR)/etc/hostname: .config
	mkdir -p $(TARGET_DIR)/etc
	echo -n > $@

$(TARGET_DIR)/etc/br-version: .config
	mkdir -p $(TARGET_DIR)/etc
	echo $(BR2_VERSION)$(shell $(TOPDIR)/scripts/setlocalversion) >$@

BCOMP = cmp -si $$(head -n 4 $(1) | wc -c):$$(head -n 4 $(2) | wc -c) $(1) $(2)

saveconfig:
	mkdir -p $(LOCAL)/$(PROJECT)
	-cp .config $(PROJECT_FILE)
	if ! $(call BCOMP,$(BUSYBOX_DIR)/.config,$(BR2_PACKAGE_BUSYBOX_CONFIG)); then \
		cp $(BUSYBOX_DIR)/.config $(BR2_PACKAGE_BUSYBOX_CONFIG); \
	fi
	if ! $(call BCOMP,$(UCLIBC_DIR)/.config,$(BR2_UCLIBC_CONFIG)); then \
		cp $(UCLIBC_DIR)/.config $(BR2_UCLIBC_CONFIG); \
	fi
	if ! $(call BCOMP,$(LINUX26_DIR)/.config,$(BR2_PACKAGE_LINUX_KCONFIG)); then \
		cp $(LINUX26_DIR)/.config $(BR2_PACKAGE_LINUX_KCONFIG); \
	fi

getconfig:
	-cp $(LOCAL)/$(PROJECT)/$(PROJECT).config .config


