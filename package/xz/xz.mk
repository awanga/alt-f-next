#############################################################
#
# xz
#
#############################################################

XZ_VERSION = 5.0.5
XZ_SITE = http://tukaani.org/xz
XZ_SOURCE = xz-$(XZ_VERSION).tar.bz2

XZ_INSTALL_STAGING = YES
XZ_INSTALL_TARGET = YES
XZ_AUTORECONF = NO
XZ_LIBTOOL_PATCH = NO
XZ_DEPENDENCIES = uclibc 

ifeq ($(BR2_PACKAGE_XZ_HOST),y)
$(eval $(call AUTOTARGETS_HOST,package,xz))
endif

ifeq ($(BR2_PACKAGE_XZ_LIBS),y)
XZ_INSTALL_STAGING = YES
XZ_INSTALL_TARGET = YES
$(eval $(call AUTOTARGETS,package,xz))
endif