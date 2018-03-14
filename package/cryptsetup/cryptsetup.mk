###########################################################
#
# cryptsetup
#
###########################################################

CRYPTSETUP_VERSION = 1.4.1
CRYPTSETUP_MAJOR = 1.4
CRYPTSETUP_SOURCE = cryptsetup-$(CRYPTSETUP_VERSION).tar.xz
CRYPTSETUP_SITE = https://www.kernel.org/pub/linux/utils/cryptsetup/v$(CRYPTSETUP_MAJOR)/
CRYPTSETUP_AUTORECONF = NO
CRYPTSETUP_INSTALL_STAGING = NO
CRYPTSETUP_INSTALL_TARGET = YES
CRYPTSETUP_LIBTOOL_PATCH = NO

CRYPTSETUP_DEPENDENCIES = lvm2 libuuid libgcrypt popt libiconv

$(eval $(call AUTOTARGETS,package,cryptsetup))
