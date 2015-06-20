################################################################################
#
# libbsd
#
################################################################################

# WARNING: not compiling, err.h (bsd) is missing from uclibc configuration

LIBBSD_VERSION = 0.7.0
LIBBSD_SOURCE = libbsd_$(LIBBSD_VERSION).orig.tar.xz
LIBBSD_SITE = $(BR2_DEBIAN_MIRROR)/debian/pool/main/libb/libbsd

LIBBSD_INSTALL_STAGING = YES
LIBBSD_INSTALL_TARGET = NO

LIBBSD_LIBTOOL_PATCH = NO

LIBBSD_CONF_OPT = --enable-static --disable-shared

$(eval $(call AUTOTARGETS,package,libbsd))

