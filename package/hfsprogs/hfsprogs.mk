#############################################################
#
# hfsprogs
#
#############################################################

# WARNING Don't create a package!
# WARNING Either fsck.hfs or the kernel are in error.
# WARNING After creating a hfs, mounting it, putting files on it and unmounting,
# WARNING if 'fsck -f' is run it ruins the fs
# This package is based on Debian patches, except for the 'bsdish' patch

HFSPROGS_VERSION:=332.25
HFSPROGS_SOURCE:=hfsprogs_$(HFSPROGS_VERSION).orig.tar.gz
HFSPROGS_SITE:=$(BR2_DEBIAN_MIRROR)/debian/pool/main/h/hfsprogs

HFSPROGS_LIBTOOL_PATCH = NO
HFSPROGS_AUTORECONF = NO

HFSPROGS_MAKE_ENV = CC="$(TARGET_CC)" CFLAGS="-I$(HFSPROGS_DIR)/include $(TARGET_CFLAGS)"
HFSPROGS_MAKE_OPT = -f Makefile.lnx 

$(eval $(call AUTOTARGETS,package,hfsprogs))

$(HFSPROGS_TARGET_CONFIGURE):
	touch $@

$(HFSPROGS_TARGET_INSTALL_TARGET):
	(cd $(HFSPROGS_DIR); \
		cp fsck_hfs.tproj/fsck_hfs $(TARGET_DIR)/usr/sbin/fsck.hfs; \
		cp newfs_hfs.tproj/newfs_hfs $(TARGET_DIR)/usr/sbin/mkfs.hfs; \
	)
	(cd $(TARGET_DIR)/usr/sbin; \
		ln -sf fsck.hfs fsck.hfsplus; \
		ln -sf mkfs.hfs mkfs.hfsplus; \
	)
	touch $@