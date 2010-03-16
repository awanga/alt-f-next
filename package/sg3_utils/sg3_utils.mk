#############################################################
#
# sg3_utils
#
#############################################################
SG3_UTILS_VERSION = 1.28
SG3_UTILS_SOURCE = sg3_utils-$(SG3_UTILS_VERSION).tar.bz2
SG3_UTILS_SITE = http://sg.danny.cz/sg/p/
SG3_UTILS_AUTORECONF = NO
SG3_UTILS_INSTALL_STAGING = NO
SG3_UTILS_INSTALL_TARGET = YES
SG3_UTILS_LIBTOOL_PATCH = NO
#SG3_UTILS_CONF_OPT =  --disable-nls --disable-gtk

SG3_UTILS_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS,package,sg3_utils))

ifeq ($(BR2_PACKAGE_SG3_UTILS),y)
TARGETS+=sg3_utils
endif