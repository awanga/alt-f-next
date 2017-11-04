#############################################################
#
# libsodium
#
############################################################

LIBSODIUM_VERSION = 1.0.15
LIBSODIUM_SOURCE = libsodium-$(LIBSODIUM_VERSION).tar.gz
LIBSODIUM_SITE = https://download.libsodium.org/libsodium/releases

LIBSODIUM_LIBTOOL_PATCH = NO
LIBSODIUM_INSTALL_STAGING = YES
LIBSODIUM_INSTALL_TARGET = YES
LIBSODIUM_CONF_OPT = --disable-static
LIBSODIUM_DEPENDENCIES = uclibc 

$(eval $(call AUTOTARGETS,package,libsodium))
