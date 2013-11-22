#############################################################
#
# mksquashfs to build to target squashfs filesystems
#
#############################################################
MKSQUASHFS_VERSION:=$(strip $(subst ",,$(BR2_TARGET_ROOTFS_MKSQUASHFS_VERSION)))
#"))
MKSQUASHFS_DIR:=$(BUILD_DIR)/squashfs$(MKSQUASHFS_VERSION)
MKSQUASHFS_SOURCE:=squashfs$(MKSQUASHFS_VERSION).tar.gz
MKSQUASHFS_SITE:=http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/squashfs
MKSQUASHFS_CAT:=$(ZCAT)

$(DL_DIR)/$(MKSQUASHFS_SOURCE):
	 $(call DOWNLOAD,$(MKSQUASHFS_SITE),$(MKSQUASHFS_SOURCE))

$(MKSQUASHFS_DIR)/.unpacked: $(DL_DIR)/$(MKSQUASHFS_SOURCE) #$(MKSQUASHFS_PATCH)
	$(MKSQUASHFS_CAT) $(DL_DIR)/$(MKSQUASHFS_SOURCE) | tar -C $(BUILD_DIR) -xvf -
	toolchain/patch-kernel.sh $(MKSQUASHFS_DIR) target/squashfs/ squashfs\*.patch
	touch $@

$(MKSQUASHFS_DIR)/squashfs-tools/mksquashfs: $(MKSQUASHFS_DIR)/.unpacked
	$(MAKE) -C $(MKSQUASHFS_DIR)/squashfs-tools

mksquashfs: $(MKSQUASHFS_DIR)/squashfs-tools/mksquashfs

mksquashfs-source: $(DL_DIR)/$(MKSQUASHFS_SOURCE)

mksquashfs-clean:
	-$(MAKE) -C $(MKSQUASHFS_DIR)/squashfs-tools clean

mksquashfs-dirclean:
	rm -rf $(MKSQUASHFS_DIR)

#############################################################
#
# Build the squashfs root filesystem image
#
#############################################################
ifeq ($(BR2_TARGET_ROOTFS_MKSQUASHFS_3),y)
# 4.x is always little endian
ifeq ($(BR2_ENDIAN),"BIG")
MKSQUASHFS_ENDIANNESS=-be
else
MKSQUASHFS_ENDIANNESS=-le
endif
endif

MKSQUASHFS_TARGET:=$(IMAGE).squashfs

squashfsroot: host-fakeroot makedevs squashfs
	# Use fakeroot to pretend all target binaries are owned by root
	rm -f $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
	touch $(PROJECT_BUILD_DIR)/.fakeroot.00000
	cat $(PROJECT_BUILD_DIR)/.fakeroot* > $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
	echo "chown -R 0:0 $(TARGET_DIR)" >> $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
ifneq ($(TARGET_DEVICE_TABLE),)
	# Use fakeroot to pretend to create all needed device nodes
	echo "$(HOST_DIR)/usr/bin/makedevs -d $(TARGET_DEVICE_TABLE) $(TARGET_DIR)" \
		>> $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
endif
	# Use fakeroot so mksquashfs believes the previous fakery
	echo "$(MKSQUASHFS_DIR)/squashfs-tools/mksquashfs " \
		    "$(TARGET_DIR) $(MKSQUASHFS_TARGET) " \
		    "-noappend $(MKSQUASHFS_ENDIANNESS)" \
		>> $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
	chmod a+x $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
	$(HOST_DIR)/usr/bin/fakeroot -- $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))
	chmod 0644 $(MKSQUASHFS_TARGET)
	-@rm -f $(PROJECT_BUILD_DIR)/_fakeroot.$(notdir $(MKSQUASHFS_TARGET))

squashfsroot-source: squashfs-source

squashfsroot-clean:
	-$(MAKE) -C $(MKSQUASHFS_DIR) clean

squashfsroot-dirclean:
	rm -rf $(MKSQUASHFS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_TARGET_ROOTFS_MKSQUASHFS),y)
TARGETS+=squashfsroot
endif
