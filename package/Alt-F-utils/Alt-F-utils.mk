#############################################################
#
# ALT_F_UTILS
#
#############################################################
ALT_F_UTILS_VERSION = 0.1
ALT_F_UTILS_SOURCE = Alt-F-utils-$(ALT_F_UTILS_VERSION).tar.gz
ALT_F_UTILS_SITE = http://localhost/~jcard
ALT_F_UTILS_DIR:=$(BUILD_DIR)/Alt-F-utils-$(ALT_F_UTILS_VERSION)
ALT_F_UTILS_AUTORECONF:=NO
ALT_F_UTILS_INSTALL_STAGING:=NO
ALT_F_UTILS_INSTALL_TARGET:=YES
ALT_F_UTILS_CAT:=$(BZCAT)
ALT_F_UTILS_BINARY:=sysctrl
ALT_F_UTILS_TARGET_BINARY:=usr/sbin/sysctrl
ALT_F_UTILS_DEPENDENCIES:=uclibc

$(DL_DIR)/$(ALT_F_UTILS_SOURCE): package/Alt-F-utils/Alt-F-utils-$(ALT_F_UTILS_VERSION)/sysctrl.c package/Alt-F-utils/Alt-F-utils-$(ALT_F_UTILS_VERSION)/dns323-fw.c
	(cd package/Alt-F-utils/; \
		tar --exclude-vcs -cvzf $(ALT_F_UTILS_SOURCE) Alt-F-utils-$(ALT_F_UTILS_VERSION); \
		cp  $(ALT_F_UTILS_SOURCE) $(DL_DIR) \
	)

Alt-F-utils-source: $(DL_DIR)/$(ALT_F_UTILS_SOURCE)

Alt-F-utils: Alt-F-utils-source

$(eval $(call AUTOTARGETS,package,Alt-F-utils))

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_ALT_F_UTILS),y)
TARGETS+=ALT_F_UTILS
endif
