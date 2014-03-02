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

FUPPES_DEPENDENCIES = uclibc pkg-config pcre libxml2 sqlite

FUPPES_CONF_ENV += MYSQL_CONFIG=no \
	PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig

FUPPES_CONF_OPT = --disable-mp4v2 --disable-transcoder-ffmpeg --disable-magickwand \
	--disable-ffmpegthumbnailer --disable-libavformat --disable-lame \
	--disable-flac --disable-vorbis --disable-mad --disable-taglib --enable-dlna 

$(eval $(call AUTOTARGETS,package/multimedia,fuppes))
