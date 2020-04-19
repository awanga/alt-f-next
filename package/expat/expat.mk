#############################################################
#
# expat
#
############################################################

EXPAT_VERSION = 2.2.5
EXPAT_SOURCE = expat-$(EXPAT_VERSION).tar.bz2
EXPAT_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/expat/expat/$(EXPAT_VERSION)

EXPAT_LIBTOOL_PATCH = NO
EXPAT_INSTALL_STAGING = YES
EXPAT_INSTALL_TARGET = YES

EXPAT_CONF_OPT = --enable-shared
EXPAT_DEPENDENCIES = uclibc host-pkgconfig

$(eval $(call AUTOTARGETS,package,expat))

$(eval $(call AUTOTARGETS_HOST,package,expat))
