###########################################################
#
# libnl
#
###########################################################

LIBNL_VERSION = 3.2.25
LIBNL_SOURCE = libnl-$(LIBNL_VERSION).tar.gz
LIBNL_SITE = https://www.infradead.org/~tgr/libnl/files

LIBNL_INSTALL_STAGING = YES
LIBNL_LIBTOOL_PATCH=NO
LIBNL_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,libnl))

$(LIBNL_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	rm -f $(TARGET_DIR)/usr/lib/libnl.so*
	rm -f $(LIBNL_TARGET_INSTALL_TARGET) $(LIBNL_HOOK_POST_INSTALL)
