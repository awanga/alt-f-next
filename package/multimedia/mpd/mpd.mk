#############################################################
#
# mpd
#
#############################################################

MPD_MAJOR_VER = 0.17
MPD_MINOR_VER = 6
MPD_VERSION = 0.17.6

MPD_SITE = http://www.musicpd.org/download/mpd/$(MPD_MAJOR_VER)
MPD_SOURCE = mpd-$(MPD_MAJOR_VER).$(MPD_MINOR_VER).tar.bz2

MPD_AUTORECONF = NO
MPD_LIBTOOL_PATCH = NO

MPD_DEPENDENCIES = uclibc flac sqlite libvorbis libogg libmad faad2 wavpack ffmpeg libcurl libid3tag alsa-lib lame twolame mpg123 libglib2 avahi

$(eval $(call AUTOTARGETS,package,mpd))

$(MPD_HOOK_POST_CONFIGURE):
	echo "#define AVCODEC_MAX_AUDIO_FRAME_SIZE 192000 // 1 second of 48khz 32bit audio" >> $(MPD_DIR)/config.h
	touch $@