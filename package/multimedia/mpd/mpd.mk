#############################################################
#
# mpd
#
#############################################################

MPD_MAJOR_VER = 0.17
MPD_MINOR_VER = 2
MPD_VERSION = 0.17.2

MPD_SITE = http://www.musicpd.org/download/mpd/$(MPD_MAJOR_VER)
MPD_SOURCE = mpd-$(MPD_MAJOR_VER).$(MPD_MINOR_VER).tar.bz2

MPD_AUTORECONF = NO
MPD_INSTALL_STAGING = NO
MPD_INSTALL_TARGET = YES
MPD_LIBTOOL_PATCH = NO

MPD_DEPENDENCIES = uclibc flac sqlite libvorbis libogg libmad ffmpeg libcurl libid3tag alsa-lib lame twolame libglib2 avahi

$(eval $(call AUTOTARGETS,package,mpd))
