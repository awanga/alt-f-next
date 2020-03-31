#############################################################
#
# lftp
#
#############################################################

LFTP_VERSION:=4.9.1
LFTP_SOURCE:=lftp-$(LFTP_VERSION).tar.xz
LFTP_SITE:=http://lftp.yar.ru/ftp

LFTP_LIBTOOL_PATCH = NO
LFTP_DEPENDENCIES = readline expat libiconv gettext openssl

LFTP_CONF_OPT = --without-gnutls --with-openssl \
	--with-readline=$(STAGING_DIR)/usr \
	--with-zlib=$(STAGING_DIR)/usr \
	--with-expat=$(STAGING_DIR)/usr

$(eval $(call AUTOTARGETS,package,lftp))

$(LFTP_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/share/applications/lftp.desktop \
		$(TARGET_DIR)/usr/share/icons/hicolor/48x48/apps/lftp-icon.png
	#rmdir $(TARGET_DIR)/usr/share/applications
