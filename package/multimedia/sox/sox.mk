################################################################################
#
# sox
#
################################################################################

SOX_VERSION = 14.4.2
SOX_SOURCE = sox-$(SOX_VERSION).tar.bz2
SOX_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/sox/sox/$(SOX_VERSION)

SOX_AUTORECONF = NO
SOX_LIBTOOL_PATCH = NO

SOX_INSTALL_STAGING = YES

SOX_DEPENDENCIES = libvorbis flac libmad lame wavpack twolame libpng libid3tag alsa-lib

SOX_CONF_OPT = --program-prefix="" --with-distro="Alt-F" --disable-openmp

$(eval $(call AUTOTARGETS,package/multimedia,sox))
