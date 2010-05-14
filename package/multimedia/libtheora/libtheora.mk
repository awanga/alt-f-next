#############################################################
#
# libtheora
#
#############################################################
LIBTHEORA_VERSION = 1.0
LIBTHEORA_SOURCE = libtheora-$(LIBTHEORA_VERSION).tar.bz2
LIBTHEORA_SITE = http://downloads.xiph.org/releases/theora
LIBTHEORA_INSTALL_STAGING = YES
LIBTHEORA_AUTORECONF = NO

# jc: need patch to Makefile.am to disable the doc subdir
# (probably only needed for someone with latex installed)

LIBTHEORA_CONF_OPT = \
		--disable-oggtest \
		--disable-vorbistest \
		--disable-sdltest \
		--disable-examples \
		--with-sdl-prefix=""

LIBTHEORA_DEPENDENCIES = libvorbis libpng libogg host-pkgconfig

$(eval $(call AUTOTARGETS,package/multimedia,libtheora))
