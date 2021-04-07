#############################################################
#
# miniupnpc
#
#############################################################
MINIUPNPC_VERSION:=2.2.2
MINIUPNPC_SOURCE:=miniupnpc-$(MINIUPNPC_VERSION).tar.gz
MINIUPNPC_SITE:=http://miniupnp.free.fr/files/

MINIUPNPC_LIBTOOL_PATCH = NO

MINIUPNPC_MAKE_ENV= CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)"
MINIUPNPC_MAKE_OPTS = upnpc-static listdevices

MINIUPNPC_INSTALL_TARGET_OPTS = DESTDIR=$(TARGET_DIR) install-static

$(eval $(autotools-package))

$(MINIUPNPC_TARGET_CONFIGURE):
	touch $@

$(MINIUPNPC_TARGET_INSTALL_TARGET):
	$(INSTALL) -m 755 $(MINIUPNPC_DIR)/upnpc-static $(TARGET_DIR)/usr/bin/upnpc
	$(INSTALL) -m 755 $(MINIUPNPC_DIR)/listdevices $(TARGET_DIR)/usr/bin/listdevices
	touch $@

# $(MINIUPNPC_HOOK_POST_INSTALL):
# 	rm -f $(TARGET_DIR)/usr/share/applications/miniupnpc.desktop \
# 		$(TARGET_DIR)/usr/share/icons/hicolor/48x48/apps/miniupnpc-icon.png
# 	#rmdir $(TARGET_DIR)/usr/share/applications
