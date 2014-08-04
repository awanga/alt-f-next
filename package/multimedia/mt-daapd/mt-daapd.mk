#############################################################
#
# mt-daapd
#
#############################################################

MT_DAAPD_VERSION = 0.2.4.2
MT_DAAPD_SOURCE = mt-daapd-$(MT_DAAPD_VERSION).tar.gz
MT_DAAPD_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/mt-daapd/mt-daapd/$(MT_DAAPD_VERSION)

MT_DAAPD_AUTORECONF = NO
MT_DAAPD_INSTALL_STAGING = NO
MT_DAAPD_INSTALL_TARGET = YES
MT_DAAPD_LIBTOOL_PATCH = YES

MT_DAAPD_DEPENDENCIES = uclibc gdbm libid3tag libvorbis

MT_DAAPD_CONF_ENV = ac_cv_func_setpgrp_void=yes
MT_DAAPD_CONF_OPT = --disable-avahi --enable-oggvorbis

$(eval $(call AUTOTARGETS,package/multimedia,mt-daapd))
