#############################################################
#
# minidlna
#
#############################################################

MINIDLNA_VERSION = 1.1.5
MINIDLNA_SOURCE = minidlna-$(MINIDLNA_VERSION).tar.gz
MINIDLNA_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/minidlna/minidlna/$(MINIDLNA_VERSION)

MINIDLNA_AUTORECONF = NO
MINIDLNA_LIBTOOL_PATCH = NO

MINIDLNA_DEPENDENCIES = uclibc libexif jpeg libid3tag flac libvorbis sqlite ffmpeg

MINIDLNA_CONF_OPT = --enable-tivo \
	--with-os-name=Alt-F \
	--with-os-version=0.1RC4.1 \
	--with-os-url=https://sourceforge.net/projects/alt-f \
	--program-prefix=""

MINIDLNA_CONF_ENV = LIBEXIF_LIBS=-lexif

$(eval $(call AUTOTARGETS,package/multimedia,minidlna))

$(MINIDLNA_HOOK_POST_CONFIGURE):
	sed -i 's|^#define USE_DAEMON.*|/* & */|' $(MINIDLNA_DIR)/config.h
	touch $@

$(MINIDLNA_HOOK_POST_INSTALL):
	mv $(TARGET_DIR)/usr/sbin/minidlnad $(TARGET_DIR)/usr/sbin/minidlna 
	touch $@