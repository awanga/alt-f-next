#############################################################
#
# sfdisk support
#
#############################################################

# This package was ripped out of the util-linux package and contains
# sfdisk version 3.0 Copyright (C) 1995  Andries E. Brouwer (aeb@cwi.nl)
# the download site does not keeps a sfdisk-$(SFDISK_VERSION).tar.bz2 version,
# only sfdisk.tar.bz2

SFDISK_VERSION:=3.0
#SFDISK_SOURCE=sfdisk-$(SFDISK_VERSION).tar.bz2
SFDISK_SOURCE=sfdisk.tar.bz2
SFDISK_CAT:=$(BZCAT)
SFDISK_SITE:=http://www.uclibc.org/
#SFDISK_DIR=$(BUILD_DIR)/sfdisk$(SFDISK_VERSION)
SFDISK_DIR=$(BUILD_DIR)/sfdisk

$(DL_DIR)/$(SFDISK_SOURCE):
	$(call DOWNLOAD,$(SFDISK_SITE),$(SFDISK_SOURCE))

$(SFDISK_DIR)/.patched: $(DL_DIR)/$(SFDISK_SOURCE)
	$(SFDISK_CAT) $(DL_DIR)/$(SFDISK_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(SFDISK_DIR) package/sfdisk/ sfdisk.\*.patch
	touch $@


$(SFDISK_DIR)/.built: $(SFDISK_DIR)/.patched
	$(MAKE) \
		CROSS=$(TARGET_CROSS) DEBUG=false OPTIMIZATION="$(TARGET_CFLAGS)" \
		-C $(SFDISK_DIR)
	-$(STRIPCMD) $(SFDISK_DIR)/sfdisk
	touch $(SFDISK_DIR)/.built

$(TARGET_DIR)/sbin/sfdisk: $(SFDISK_DIR)/.built
	cp $(SFDISK_DIR)/sfdisk $(TARGET_DIR)/sbin/sfdisk
	touch -c $(TARGET_DIR)/sbin/sfdisk

sfdisk: uclibc $(TARGET_DIR)/sbin/sfdisk

sfdisk-source: $(DL_DIR)/$(SFDISK_SOURCE)

sfdisk-clean:
	rm -f $(TARGET_DIR)/sbin/sfdisk
	-$(MAKE) -C $(SFDISK_DIR) clean

sfdisk-dirclean:
	rm -rf $(SFDISK_DIR)
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_SFDISK),y)
TARGETS+=sfdisk
endif
