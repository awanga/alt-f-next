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

FUPPES__DEPENDENCIES = uclibc pcre libxml2 sqlite ffmpeg taglib flac libmad taglib

FUPPES_CONF_ENV += MYSQL_CONFIG=no PKG_CONFIG_PATH=$(STAGING_DIR)/usr/lib/pkgconfig/ TAGLIB_CONFIG=$(STAGING_DIR)/usr/bin/taglib-config

FUPPES_LIBTOOL_PATCH = NO
FUPPES_AUTORECONF = NO

# searching for mad.pc config in libmad... patch/create one :-(
# taglib is using system header files - install host taglib-devel :-(
# create lame/twolame buildroot package

FUPPES_CONF_OPT = --disable-mp4v2 --enable-transcoder-ffmpeg --enable-mad

$(eval $(call AUTOTARGETS,package/multimedia,fuppes))
