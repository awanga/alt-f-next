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
FUPPES_LIBTOOL_PATCH = NO
FUPPES_AUTORECONF = NO

FUPPES_DEPENDENCIES = uclibc pkg-config pcre libxml2 sqlite ffmpeg taglib flac libvorbis libmad taglib lame ffmpegthumbnailer

FUPPES_CONF_ENV += MYSQL_CONFIG=no \
 TAGLIB_CONFIG=$(STAGING_DIR)/usr/bin/taglib-config \
 MAD_CFLAGS=" " MAD_LIBS=-lmad \
 PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig \
 FFMPEGTHUMBNAILER_CFLAGS=-I$(STAGING_DIR)/usr/include/libffmpegthumbnailer

FUPPES_CONF_OPT = --disable-mp4v2 --enable-transcoder-ffmpeg --enable-mad --enable-lame --disable-ffmpegthumbnailer

#--enable-ffmpegthumbnailer

$(eval $(call AUTOTARGETS,package/multimedia,fuppes))
