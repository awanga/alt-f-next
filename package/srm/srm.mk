#############################################################
#
# srm
#
#############################################################

SRM_VERSION:=1.2.15
SRM_SOURCE:=srm-$(SRM_VERSION).tar.gz
SRM_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/srm/$(SRM_VERSION)

SRM_LIBTOOL_PATCH = NO
SRM_INSTALL_STAGING = NO

$(eval $(call AUTOTARGETS,package,srm))

$(SRM_HOOK_POST_INSTALL):
	$(RM) $(TARGET_DIR)/usr/bin/fill_test
	touch $@
