#############################################################
#
# ntfs-3g
#
#############################################################

NTFS_3G_VERSION:=2012.1.15
NTFS_3G_SOURCE:=ntfs-3g_ntfsprogs-$(NTFS_3G_VERSION).tgz
#NTFS_3G_SITE:=http://tuxera.com/opensource
NTFS_3G_SITE:=http://sources.openelec.tv/mirror/ntfs-3g_ntfsprogs

NTFS_3G_CONF_OPT = --libdir=/usr/lib --disable-ldconfig --disable-mtab --program-prefix=""
# save 25KB:
#TARGET_CFLAGS += -Os

NTFS_3G_EXTRA_BIN = ntfscat ntfscluster ntfscmp ntfsfix ntfsinfo ntfsls \
	lowntfs-3g ntfs-3g.secaudit ntfs-3g.usermap ntfs-3g.probe
NTFS_3G_EXTRA_SBIN = mkntfs ntfsclone ntfscp ntfslabel ntfsresize ntfsundelete
NTFS_3G_NO = mkfs.ntfs mount.lowntfs-3g mount.ntfs-3g

$(eval $(call AUTOTARGETS,package,ntfs-3g))

$(NTFS_3G_HOOK_POST_INSTALL):
ifeq ($(BR2_PACKAGE_NTFS_3G_NTFSPROGS),)
	( cd $(TARGET_DIR); \
	for i in $(NTFS_3G_EXTRA_BIN); do rm usr/bin/$$i; done; \
	for i in $(NTFS_3G_EXTRA_SBIN); do rm usr/sbin/$$i; done; \
	)
endif
	( cd $(TARGET_DIR); \
	for i in $(NTFS_3G_NO); do rm sbin/$$i; done; \
	)
	touch $@

