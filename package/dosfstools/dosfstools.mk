#############################################################
#
# dosfstools
#
#############################################################

# 3.0.17 to 3.0.24 uses htole16 htole32 le16toh le32toh, that uclibc does not has

DOSFSTOOLS_VERSION:=3.0.24
DOSFSTOOLS_SOURCE:=dosfstools-$(DOSFSTOOLS_VERSION).tar.gz

# original site inactive. Alternatives:
# http://sources.buildroot.net, http://fossies.org/linux/misc/
DOSFSTOOLS_SITE:=http://daniel-baumann.ch/files/software/dosfstools

DOSFSTOOLS_DIR:=$(BUILD_DIR)/dosfstools-$(DOSFSTOOLS_VERSION)
DOSFSTOOLS_CAT:=$(ZCAT)

# pre 3.0.24 names
#MKDOSFS_BINARY:=mkdosfs
#MKDOSFS_TARGET_BINARY:=sbin/mkdosfs
#DOSFSCK_BINARY:=dosfsck
#DOSFSCK_TARGET_BINARY:=sbin/dosfsck
#DOSFSLABEL_BINARY:=dosfslabel
#DOSFSLABEL_TARGET_BINARY:=sbin/dosfslabel

# in 3.0.24 those are the new names: mkfs.fat fsck.fat fatlabel
MKDOSFS_BINARY:=mkfs.fat
MKDOSFS_TARGET_BINARY:=sbin/mkdosfs
DOSFSCK_BINARY:=fsck.fat
DOSFSCK_TARGET_BINARY:=sbin/dosfsck
DOSFSLABEL_BINARY:=fatlabel
DOSFSLABEL_TARGET_BINARY:=sbin/dosfslabel
DOSFSLIB_BINARY:=libfat.so
DOSFSLIB_TARGET_BINARY:=usr/lib/libfat.so

$(DL_DIR)/$(DOSFSTOOLS_SOURCE):
	 $(call DOWNLOAD,$(DOSFSTOOLS_SITE),$(DOSFSTOOLS_SOURCE))

dosfstools-source: $(DL_DIR)/$(DOSFSTOOLS_SOURCE)

$(DOSFSTOOLS_DIR)/.unpacked: $(DL_DIR)/$(DOSFSTOOLS_SOURCE) $(wildcard local/dosfstools/dosfstools*.patch)
	$(DOSFSTOOLS_CAT) $(DL_DIR)/$(DOSFSTOOLS_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(DOSFSTOOLS_DIR) package/dosfstools/ dosfstools-$(DOSFSTOOLS_VERSION)\*.patch
	touch $(DOSFSTOOLS_DIR)/.unpacked

# uclibc does not has htobexx 
# missing: htole16 htole32 le16toh le32toh
#define htobe32(a) htonl((a))
#define htobe16(a) htons((a))
#define be16toh(a) ntohs((a))
#define be32toh(a) ntohl((a))

$(DOSFSTOOLS_DIR)/.built : $(DOSFSTOOLS_DIR)/.unpacked
	$(MAKE) \
		CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		LD="$(TARGET_LD)" \
		LDLIBS="-liconv" \
		-C $(DOSFSTOOLS_DIR)
	$(STRIPCMD) $(DOSFSTOOLS_DIR)/$(MKDOSFS_BINARY)
	$(STRIPCMD) $(DOSFSTOOLS_DIR)/$(DOSFSCK_BINARY)
	$(STRIPCMD) $(DOSFSTOOLS_DIR)/$(DOSFSLABEL_BINARY)
	$(STRIPCMD) $(DOSFSTOOLS_DIR)/$(DOSFSLIB_BINARY)
	touch $@

$(TARGET_DIR)/$(DOSFSLIB_TARGET_BINARY): $(DOSFSTOOLS_DIR)/.built
	cp -a $(DOSFSTOOLS_DIR)/$(DOSFSLIB_BINARY) $(TARGET_DIR)/$(DOSFSLIB_TARGET_BINARY)
	touch -c $@

$(TARGET_DIR)/$(MKDOSFS_TARGET_BINARY): $(TARGET_DIR)/$(DOSFSLIB_TARGET_BINARY) $(DOSFSTOOLS_DIR)/.built
	cp -a $(DOSFSTOOLS_DIR)/$(MKDOSFS_BINARY) $@
	touch -c $@

$(TARGET_DIR)/$(DOSFSCK_TARGET_BINARY): $(TARGET_DIR)/$(DOSFSLIB_TARGET_BINARY) $(DOSFSTOOLS_DIR)/.built
	cp -a $(DOSFSTOOLS_DIR)/$(DOSFSCK_BINARY) $@
	touch -c $@

$(TARGET_DIR)/$(DOSFSLABEL_TARGET_BINARY): $(TARGET_DIR)/$(DOSFSLIB_TARGET_BINARY) $(DOSFSTOOLS_DIR)/.built
	cp -a $(DOSFSTOOLS_DIR)/$(DOSFSLABEL_BINARY) $@
	touch -c $@

dosfstools: uclibc libiconv $(TARGET_DIR)/$(DOSFSTOOLS_TARGET_BINARY) $(TARGET_DIR)/$(DOSFSCK_TARGET_BINARY)

dosfstools-build: $(DOSFSTOOLS_DIR)/.built

dosfstools-clean:
	rm -f $(TARGET_DIR)/$(MKDOSFS_TARGET_BINARY)
	rm -f $(TARGET_DIR)/$(DOSFSCK_TARGET_BINARY)
	rm -f $(TARGET_DIR)/$(DOSFSLABEL_TARGET_BINARY)
	-$(MAKE) -C $(DOSFSTOOLS_DIR) clean

dosfstools-dirclean:
	rm -rf $(DOSFSTOOLS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_DOSFSTOOLS_MKDOSFS),y)
TARGETS+=$(TARGET_DIR)/$(MKDOSFS_TARGET_BINARY)
endif

ifeq ($(BR2_PACKAGE_DOSFSTOOLS_DOSFSCK),y)
TARGETS+=$(TARGET_DIR)/$(DOSFSCK_TARGET_BINARY)
endif

ifeq ($(BR2_PACKAGE_DOSFSTOOLS_DOSFSLABEL),y)
TARGETS+=$(TARGET_DIR)/$(DOSFSLABEL_TARGET_BINARY)
endif
