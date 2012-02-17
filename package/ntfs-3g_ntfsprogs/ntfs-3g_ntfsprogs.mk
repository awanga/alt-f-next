#############################################################
#
# ntfs-3g_ntfsprogs
#
#############################################################

#NTFS_3G_NTFSPROGS_VERSION:=2011.4.12
NTFS_3G_NTFSPROGS_VERSION:=2012.1.15
NTFS_3G_NTFSPROGS_SOURCE:=ntfs-3g_ntfsprogs-$(NTFS_3G_NTFSPROGS_VERSION).tgz
NTFS_3G_NTFSPROGS_SITE:=http://tuxera.com/opensource
NTFS_3G_NTFSPROGS_INSTALL_STAGING:=yes
NTFS_3G_NTFSPROGS_CONF_OPT = --libdir=/usr/lib --disable-ldconfig --disable-mtab --program-prefix=""

ifeq ($(BR2_PACKAGE_NTFS_3G_NTFSPROGS_NTFSPROGS),)
NTFS_3G_NTFSPROGS_CONF_OPT += --disable-ntfsprogs
endif

$(eval $(call AUTOTARGETS,package,ntfs-3g_ntfsprogs))

ifeq ($(BR2_PACKAGE_NTFS_3G_NTFSPROGS_NTFSPROGS),)
$(NTFS_3G_NTFSPROGS_TARGET_INSTALL_TARGET): $(NTFS_3G_NTFSPROGS_TARGET_INSTALL_STAGING)
	cp -dpf $(STAGING_DIR)/usr/lib/libntfs-3g.so* $(TARGET_DIR)/usr/lib/
	$(INSTALL) -m 0755 $(STAGING_DIR)/usr/bin/ntfs-3g $(TARGET_DIR)/usr/bin/
	touch $@
endif

$(NTFS_3G_NTFSPROGS_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(NTFS_3G_NTFSPROGS_DIR) uninstall
	rm -f $(TARGET_DIR)/usr/lib/libntfs-3g*
	rm -f $(TARGET_DIR)/usr/bin/ntfs-3g $(TARGET_DIR)/usr/bin/ntfs-3g.probe
	rm -f $(NTFS_3G_NTFSPROGS_TARGET_INSTALL_STAGING) $(NTFS_3G_NTFSPROGS_TARGET_INSTALL_TARGET) $(NTFS_3G_NTFSPROGS_HOOK_POST_INSTALL)
