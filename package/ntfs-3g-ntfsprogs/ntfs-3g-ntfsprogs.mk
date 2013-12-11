#############################################################
#
# ntfs-3g-ntfsprogs
#
#############################################################

NTFS_3G_NTFSPROGS_VERSION:=2012.1.15
NTFS_3G_NTFSPROGS_SOURCE:=ntfs-3g_ntfsprogs-$(NTFS_3G_NTFSPROGS_VERSION).tgz
NTFS_3G_NTFSPROGS_SITE:=http://tuxera.com/opensource

NTFS_3G_NTFSPROGS_CONF_OPT = --libdir=/usr/lib --disable-ldconfig --disable-mtab --program-prefix=""

NTFS_3G_NTFSPROGS_EXTRA_BIN = ntfscat ntfscluster ntfscmp ntfsfix ntfsinfo ntfsls \
	lowntfs-3g ntfs-3g.secaudit ntfs-3g.usermap ntfs-3g.probe
NTFS_3G_NTFSPROGS_EXTRA_SBIN = mkntfs ntfsclone ntfscp ntfslabel ntfsresize ntfsundelete
NTFS_3G_NTFSPROGS_NO = mkfs.ntfs mount.lowntfs-3g mount.ntfs-3g

$(eval $(call AUTOTARGETS,package,ntfs-3g-ntfsprogs))

$(NTFS_3G_NTFSPROGS_HOOK_POST_INSTALL):
ifeq ($(BR2_PACKAGE_NTFS_3G_NTFSPROGS_NTFSPROGS),)
	( cd $(TARGET_DIR); \
	for i in $(NTFS_3G_NTFSPROGS_EXTRA_BIN); do rm usr/bin/$$i; done; \
	for i in $(NTFS_3G_NTFSPROGS_EXTRA_SBIN); do rm usr/sbin/$$i; done; \
	)
endif
	( cd $(TARGET_DIR); \
	for i in $(NTFS_3G_NTFSPROGS_NO); do rm sbin/$$i; done; \
	)
	touch $@

