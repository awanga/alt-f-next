#############################################################
#
# wxwidgets
#
#############################################################

#WXWIDGETS_VERSION:=3.0.1
#WXWIDGETS_VERSION:=2.9.5
WXWIDGETS_VERSION:=2.8.12
WXWIDGETS_MAJOR=2.8

WXWIDGETS_SOURCE:=wxWidgets-$(WXWIDGETS_VERSION).tar.bz2
WXWIDGETS_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/wxwindows/$(WXWIDGETS_VERSION)

WXWIDGETS_LIBTOOL_PATCH = NO
WXWIDGETS_INSTALL_STAGING = YES

WXWIDGETS_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

WXWIDGETS_CONF_OPT = --disable-gui --without-subdirs \
	--enable-optimise --enable-monolithic --enable-unicode

$(eval $(call AUTOTARGETS,package,wxwidgets))

$(WXWIDGETS_HOOK_POST_INSTALL):
	(cd $(TARGET_DIR); rm -rf ./usr/lib/wx ./usr/share/bakefile ./usr/bin/wx-config )
	ln -sf $(STAGING_DIR)/usr/lib/wx/config/arm-linux-base-unicode-release-$(WXWIDGETS_MAJOR) \
		$(STAGING_DIR)/usr/bin/wx-config
	cp $(STAGING_DIR)/usr/lib/wx/include/arm-linux-base-unicode-release-$(WXWIDGETS_MAJOR)/wx/setup.h \
		$(STAGING_DIR)/usr/include/wx-$(WXWIDGETS_MAJOR)/wx
	touch $@