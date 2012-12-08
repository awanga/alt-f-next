#############################################################
#
# mpd
#
#############################################################

MPD_VERSION = 0.17.2
MPD_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/project/musicpd/mpd/$(MPD_VERSION)
MPD_SOURCE = mpd-$(MPD_VERSION).tar.bz2

MPD_AUTORECONF = NO
MPD_INSTALL_STAGING = NO
MPD_INSTALL_TARGET = YES
MPD_LIBTOOL_PATCH = NO

MPD_DEPENDENCIES = uclibc flac sqlite libvorbis libogg libmad ffmpeg libcurl libid3tag alsa-lib lame twolame libglib2 avahi

#MPD_CONF_OPT = --with-zeroconf=avahi
#MPD_CONF_ENV = AVAHI_LIBS="-lavahi-common -lavahi-client" AVAHI_CFLAGS=" "

$(eval $(call AUTOTARGETS,package,mpd))
