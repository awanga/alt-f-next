#############################################################
#
# automatic
#
#############################################################

#CRYPTSETUP_VERSION = 1.3.1
CRYPTSETUP_VERSION = 1.4.1
CRYPTSETUP_SOURCE = cryptsetup-$(CRYPTSETUP_VERSION).tar.bz2
CRYPTSETUP_SITE = http://cryptsetup.googlecode.com/files
CRYPTSETUP_AUTORECONF = NO
CRYPTSETUP_INSTALL_STAGING = NO
CRYPTSETUP_INSTALL_TARGET = YES
CRYPTSETUP_LIBTOOL_PATCH = NO

CRYPTSETUP_DEPENDENCIES = lvm2 libuuid libgcrypt popt libiconv

$(eval $(call AUTOTARGETS,package,cryptsetup))
