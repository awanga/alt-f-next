#############################################################
#
# MediaTomb
#
#############################################################

MEDIATOMB_VERSION = 0.12.1
MEDIATOMB_SOURCE = mediatomb-$(MEDIATOMB_VERSION).tar.gz
MEDIATOMB_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/mediatomb/MediaTomb/$(MEDIATOMB_VERSION)

MEDIATOMB_LIBTOOL_PATCH = NO
MEDIATOMB_DEPENDENCIES = uclibc sqlite mysql expat file taglib ffmpeg libcurl

MEDIATOMB_CONF_OPT = --enable-sighup --enable-inotify

$(eval $(call AUTOTARGETS,package/multimedia,mediatomb))

