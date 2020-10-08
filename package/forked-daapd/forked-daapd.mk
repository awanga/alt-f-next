################################################################################
#
# forked-daapd
#
################################################################################

FORKED_DAAPD_VERSION = 26.4
FORKED_DAAPD_SITE = https://github.com/ejurgensen/forked-daapd/releases/download/$(FORKED_DAAPD_VERSION)
FORKED_DAAPD_SOURCE = forked-daapd-$(FORKED_DAAPD_VERSION).tar.xz
FORKED_DAAPD_AUTORECONF = YES
FORKED_DAAPD_LICENSE = GPL-2.0
FORKED_DAAPD_LICENSE_FILES = COPYING

FORKED_DAAPD_DEPENDENCIES = \
	alsa-lib \
	avahi \
	ffmpeg \
	libantlr3 \
	libconfuse \
	libcurl \
	libevent \
	libgcrypt \
	libunistring \
	mxml \
	sqlite

FORKED_DAAPD_CONF_OPTS = \
	--prefix=/usr \
	--with-gnu-ld \
	--enable-itunes \
	--enable-lastfm \
	--enable-mpd \
	--disable-verification \
	--disable-webinterface \
	--disable-spotify \
	--with-alsa \
	--with-avahi \
	--without-pulseaudio \
	--without-libevent_pthreads

$(eval $(autotools-package))
