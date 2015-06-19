################################################################################
#
# wavpack
#
################################################################################

WAVPACK_VERSION = 4.70.0
WAVPACK_SITE = http://www.wavpack.com
WAVPACK_SOURCE = wavpack-$(WAVPACK_VERSION).tar.bz2

WAVPACK_AUTORECONF = YES
WAVPACK_LIBTOOL_PATCH = NO

WAVPACK_INSTALL_STAGING = YES

WAVPACK_DEPENDENCIES = libiconv

$(eval $(call AUTOTARGETS,package/multimedia,wavpack))