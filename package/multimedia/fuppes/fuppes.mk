#############################################################
#
# fuppes
#
#############################################################

FUPPES_VERSION = 660
FUPPES_SOURCE = fuppes-0.$(FUPPES_VERSION).tar.gz
FUPPES_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/fuppes/fuppes/SVN-$(FUPPES_VERSION)

FUPPES_LIBTOOL_PATCH = NO
FUPPES_AUTORECONF = YES

FUPPES_DEPENDENCIES = uclibc pkg-config pcre libxml2 sqlite

FUPPES_CONF_ENV += MYSQL_CONFIG=no

FUPPES_CONF_OPT = --disable-mp4v2 --disable-transcoder-ffmpeg --disable-magickwand \
	--disable-ffmpegthumbnailer --disable-libavformat --disable-lame \
	--disable-flac --disable-vorbis --disable-mad --disable-taglib --enable-dlna 

$(eval $(call AUTOTARGETS,package/multimedia,fuppes))
