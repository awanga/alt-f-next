#############################################################
#
# htop
#
#############################################################

HTOP_VERSION:=1.0.2
HTOP_SOURCE:=htop-$(HTOP_VERSION).tar.gz
HTOP_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/htop/htop/$(HTOP_VERSION)

HTOP_LIBTOOL_PATCH = NO

HTOP_DEPENDENCIES = ncurses
HTOP_CONF_OPT = --disable-unicode --program-prefix=""

$(eval $(call AUTOTARGETS,package,htop))

$(HTOP_HOOK_POST_INSTALL):
	-rm -rf $(TARGET_DIR)/usr/share/applications
	-rm -rf $(TARGET_DIR)/usr/share/pixmaps
	touch $@