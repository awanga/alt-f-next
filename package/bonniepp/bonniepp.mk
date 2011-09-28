#############################################################
#
# bonniepp
#
#############################################################
BONNIEPP_VERSION:=1.03e
BONNIEPP_SOURCE:=bonnie++-$(BONNIEPP_VERSION).tgz
BONNIEPP_SITE:=http://www.coker.com.au/bonnie++
BONNIEPP_DIR:=$(BUILD_DIR)/bonnie++-$(BONNIEPP_VERSION)
BONNIEPP_INSTALL_STAGING = NO

$(eval $(call AUTOTARGETS,package,bonniepp))

$(BONNIEPP_HOOK_POST_CONFIGURE):

$(BONNIEPP_TARGET_INSTALL_TARGET):
	(cd $(BONNIEPP_DIR); cp bonnie++ zcav $(TARGET_DIR)/usr/sbin)
	touch $@
