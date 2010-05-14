#############################################################
#
# fuppes
#
#############################################################
FUPPES_VERSION = 660
FUPPES_SOURCE = fuppes-0.$(FUPPES_VERSION).tar.gz
FUPPES_SITE = http://downloads.sourceforge.net/project/fuppes/fuppes/SVN-$(FUPPES_VERSION)
FUPPES_INSTALL_STAGING = NO
FUPPES_INSTALL_TARGET = YES

FUPPES_DEPENDENCIES = uclibc host-pkgconfig pcre libxml2 sqlite ffmpeg taglib flac libvorbis libmad taglib lame

# taglib is using system header files - install host taglib-devel :-(
# create twolame buildroot package?

FUPPES_CONF_ENV += MYSQL_CONFIG=no \
	TAGLIB_CONFIG=$(STAGING_DIR)/usr/bin/taglib-config \
	MAD_CFLAGS=" " MAD_LIBS=-lmad

FUPPES_LIBTOOL_PATCH = NO
FUPPES_AUTORECONF = NO

FUPPES_CONF_OPT = --disable-mp4v2 --enable-transcoder-ffmpeg --enable-mad --enable-lame

$(eval $(call AUTOTARGETS,package/multimedia,fuppes))
