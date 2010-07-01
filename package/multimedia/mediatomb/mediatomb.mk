#############################################################
#
# MediaTomb
#
#############################################################
MEDIATOMB_VERSION = 0.11.0
MEDIATOMB_SOURCE = mediatomb-$(MEDIATOMB_VERSION).tar.gz
MEDIATOMB_SITE = http://downloads.sourceforge.net/project/mediatomb/MediaTomb/0.11.0/
MEDIATOMB_AUTORECONF = YES
MEDIATOMB_INSTALL_STAGING = NO
MEDIATOMB_INSTALL_TARGET = YES
MEDIATOMB_LIBTOOL_PATCH = NO
MEDIATOMB_DEPENDENCIES = uclibc sqlite expat file taglib ffmpeg curl

MEDIATOMB_CONF_OPT = --enable-sighup

$(eval $(call AUTOTARGETS,package/multimedia,mediatomb))

