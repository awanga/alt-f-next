#############################################################
#
# dosfstools
#
#############################################################

# uses htole16 htole32 le16toh le32toh, that uclibc does not has

DOSFSTOOLS_VERSION:=3.0.28
DOSFSTOOLS_SOURCE:=dosfstools-$(DOSFSTOOLS_VERSION).tar.xz
DOSFSTOOLS_SITE:=https://github.com/dosfstools/dosfstools/releases/download/v$(DOSFSTOOLS_VERSION)

DOSFSTOOLS_DEPENDENCIES:=uclibc libiconv

# FIXME: in 3.0.24 and latter those are the new names: mkfs.fat fsck.fat fatlabel
MKDOSFS_BINARY:=mkfs.fat
MKDOSFS_TARGET_BINARY:=usr/sbin/mkdosfs
DOSFSCK_BINARY:=fsck.fat
DOSFSCK_TARGET_BINARY:=usr/sbin/dosfsck
DOSFSLABEL_BINARY:=fatlabel
DOSFSLABEL_TARGET_BINARY:=usr/sbin/dosfslabel
DOSFSLIB_BINARY:=libfat.so
DOSFSLIB_TARGET_BINARY:=usr/lib/libfat.so

DOSFSTOOLS_MAKE_OPT:=CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)" LD="$(TARGET_LD)" LDLIBS="-liconv"

$(eval $(call AUTOTARGETS,package,dosfstools))

$(DOSFSTOOLS_TARGET_CONFIGURE):
	touch $@

$(DOSFSTOOLS_TARGET_INSTALL_TARGET):
	cp -a $(DOSFSTOOLS_DIR)/$(DOSFSLIB_BINARY) $(TARGET_DIR)/$(DOSFSLIB_TARGET_BINARY)
	cp -a $(DOSFSTOOLS_DIR)/$(DOSFSCK_BINARY) $(TARGET_DIR)/$(DOSFSCK_TARGET_BINARY)
	cp -a $(DOSFSTOOLS_DIR)/$(DOSFSLABEL_BINARY) $(TARGET_DIR)/$(DOSFSLABEL_TARGET_BINARY)
	# use busybox mkfs.vfat 
	# cp -a $(DOSFSTOOLS_DIR)/$(MKDOSFS_BINARY) $(TARGET_DIR)/$(MKDOSFS_TARGET_BINARY)
	touch -c $@
