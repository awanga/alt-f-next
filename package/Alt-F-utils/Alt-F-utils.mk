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

$(eval $(call AUTOTARGETS,package,Alt-F-utils))

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_ALT_F_UTILS),y)
TARGETS+=ALT_F_UTILS
endif
