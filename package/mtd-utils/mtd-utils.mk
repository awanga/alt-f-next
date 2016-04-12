#############################################################
#
# mtd-utils provides mtd and jffs2 utilities
#
#############################################################

MTD_UTILS_VERSION:=1.5.0
MTD_UTILS_SOURCE:=mtd-utils-$(MTD_UTILS_VERSION).tar.bz2
MTD_UTILS_SITE:=ftp://ftp.infradead.org/pub/mtd-utils
MTD_UTILS_NAME:=mtd-utils-$(MTD_UTILS_VERSION)
MTD_UTILS_HOST_DIR:= $(BUILD_DIR)/$(MTD_UTILS_NAME)_host
MTD_UTILS_DIR:=$(BUILD_DIR)/$(MTD_UTILS_NAME)
MTD_UTILS_CAT:=$(BZCAT)

#############################################################
#
# Build mkfs.jffs2 and sumtool for use on the local host system if
# needed by target/jffs2root.
#
#############################################################
MKFS_JFFS2 := $(MTD_UTILS_HOST_DIR)/mkfs.jffs2
SUMTOOL := $(MTD_UTILS_HOST_DIR)/sumtool

$(DL_DIR)/$(MTD_UTILS_SOURCE):
	$(call DOWNLOAD,$(MTD_UTILS_SITE),$(MTD_UTILS_SOURCE))

$(MTD_UTILS_HOST_DIR)/.unpacked: $(DL_DIR)/$(MTD_UTILS_SOURCE)
	$(MTD_UTILS_CAT) $(DL_DIR)/$(MTD_UTILS_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	rm -rf $(MTD_UTILS_HOST_DIR)
	mv $(BUILD_DIR)/$(MTD_UTILS_NAME) $(MTD_UTILS_HOST_DIR)
	toolchain/patch-kernel.sh $(MTD_UTILS_HOST_DIR) \
		package/mtd-utils mtd-utils-$(MTD_UTILS_VERSION)-all\*.patch
	toolchain/patch-kernel.sh $(MTD_UTILS_HOST_DIR) \
		package/mtd-utils mtd-utils-$(MTD_UTILS_VERSION)-host\*.patch
	touch $@

$(MKFS_JFFS2): $(MTD_UTILS_HOST_DIR)/.unpacked $(STAMP_DIR)/host_lzo_installed
	CC="$(HOSTCC)" CROSS= LDFLAGS=-L$(HOST_DIR)/usr/lib \
		$(MAKE) CFLAGS='-I$(HOST_DIR)/usr/include -I./include' \
		LINUXDIR=$(LINUX_DIR) BUILDDIR=$(MTD_UTILS_HOST_DIR) \
		-C $(MTD_UTILS_HOST_DIR) DESTDIR=$(HOST_DIR) install
	

mtd-utils-host: $(MKFS_JFFS2)

mtd-utils-host-source: $(DL_DIR)/$(MTD_UTILS_SOURCE)

mtd-utils-host-clean:
	-$(MAKE) -C $(MTD_UTILS_HOST_DIR) clean

mtd-utils-host-dirclean:
	rm -rf $(MTD_UTILS_HOST_DIR)

#############################################################
#
# build mtd for use on the target system
#
#############################################################
$(MTD_UTILS_DIR)/.unpacked: $(DL_DIR)/$(MTD_UTILS_SOURCE)
	$(MTD_UTILS_CAT) $(DL_DIR)/$(MTD_UTILS_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	#mv $(BUILD_DIR)/$(MTD_UTILS_NAME) $(MTD_UTILS_DIR)
	toolchain/patch-kernel.sh $(MTD_UTILS_DIR) package/mtd-utils mtd-utils-$(MTD_UTILS_VERSION)-all\*.patch
	toolchain/patch-kernel.sh $(MTD_UTILS_DIR) package/mtd-utils mtd-utils-$(MTD_UTILS_VERSION)-target\*.patch
	touch $@

MTD_UTILS_TARGETS_n :=
MTD_UTILS_TARGETS_y :=

MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_DOCFDISK)		+= docfdisk
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_DOC_LOADBIOS)		+= doc_loadbios
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASHCP)		+= flashcp
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_ERASE)		+= flash_erase
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_ERASEALL) 	+= flash_eraseall
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_LOCK)		+= flash_lock
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_OTP_DUMP)	+= flash_otp_dump
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_OTP_INFO)	+= flash_otp_info
#MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_OTP_LOCK)	+= flash_otp_lock
#MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_OTP_WRITE)	+= flash_otp_write
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FLASH_UNLOCK)	+= flash_unlock
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FTL_CHECK)	+= ftl_check
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_FTL_FORMAT)	+= ftl_format
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_JFFS2DUMP)	+= jffs2dump
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_MKFSJFFS2)	+= mkfs.jffs2
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_MTD_DEBUG)	+= mtd_debug
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_NANDDUMP)	+= nanddump
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_NANDTEST)	+= nandtest
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_NANDWRITE)	+= nandwrite
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_NFTLDUMP)	+= nftldump
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_NFTL_FORMAT)	+= nftl_format
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_RECV_IMAGE)	+= recv_image
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_RFDDUMP)	+= rfddump
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_RFDFORMAT)	+= rfdformat
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_SERVE_IMAGE)	+= serve_image
MTD_UTILS_TARGETS_$(BR2_PACKAGE_MTD_UTILS_SUMTOOL)	+= sumtool

MTD_UTILS_TARGETS_UBIFS_$(BR2_PACKAGE_MTD_UTILS_MKFSUBIFS)	+= mkfs.ubifs
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_MTDINFO)		+= mtdinfo
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIATTACH)	+= ubiattach
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBICRC32)		+= ubicrc32
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIDETACH)	+= ubidetach
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIFORMAT)	+= ubiformat
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIMKVOL)		+= ubimkvol
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBINFO)		+= ubinfo
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBINIZE)		+= ubinize
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIRENAME)	+= ubirename
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIRMVOL)		+= ubirmvol
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIRSVOL)		+= ubirsvol
MTD_UTILS_TARGETS_UBI_$(BR2_PACKAGE_MTD_UTILS_UBIUPDATEVOL)	+= ubiupdatevol

MTD_UTILS_TARGETS_y += $(addprefix ubi-utils/,$(MTD_UTILS_TARGETS_UBI_y))
MTD_UTILS_TARGETS_y += $(addprefix mkfs.ubifs/,$(MTD_UTILS_TARGETS_UBIFS_y))

MTD_UTILS_BUILD_TARGETS := $(addprefix $(MTD_UTILS_DIR)/, $(MTD_UTILS_TARGETS_y))

$(MTD_UTILS_BUILD_TARGETS): $(MTD_UTILS_DIR)/.unpacked
	mkdir -p $(TARGET_DIR)/usr/sbin
	$(MAKE) CFLAGS="-I. -I./include -I$(LINUX_HEADERS_DIR)/include -I$(STAGING_DIR)/usr/include $(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		BUILDDIR=$(MTD_UTILS_DIR) \
		CROSS=$(TARGET_CROSS) CC=$(TARGET_CC) LINUXDIR=$(LINUX26_DIR) \
		WITHOUT_XATTR=1 WITHOUT_LARGEFILE=1 -C $(MTD_UTILS_DIR)

MTD_UTILS_TARGETS := $(addprefix $(TARGET_DIR)/usr/sbin/, $(MTD_UTILS_TARGETS_y))

$(MTD_UTILS_TARGETS): $(TARGET_DIR)/usr/sbin/% : $(MTD_UTILS_DIR)/%
	cp -f $< $(TARGET_DIR)/usr/sbin/$(notdir $@)
	$(STRIPCMD) $(TARGET_DIR)/usr/sbin/$(notdir $@)

mtd-utils: zlib lzo libuuid $(MTD_UTILS_TARGETS)

mtd-utils-source: $(DL_DIR)/$(MTD_UTILS_SOURCE)

mtd-utils-clean:
	-$(MAKE) -C $(MTD_UTILS_DIR) clean

mtd-utils-dirclean:
	rm -rf $(MTD_UTILS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_MTD_UTILS),y)
TARGETS+=mtd-utils
endif
