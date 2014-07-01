#############################################################
#
# minidlna
#
#############################################################

MINIDLNA_VERSION = 1.1.3
MINIDLNA_SOURCE = minidlna-$(MINIDLNA_VERSION).tar.gz
MINIDLNA_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/minidlna/minidlna/$(MINIDLNA_VERSION)

MINIDLNA_AUTORECONF = NO
MINIDLNA_LIBTOOL_PATCH = NO

MINIDLNA_INSTALL_STAGING = NO
MINIDLNA_INSTALL_TARGET = YES

MINIDLNA_DEPENDENCIES = uclibc libexif jpeg libid3tag flac libvorbis sqlite ffmpeg

MINIDLNA_CONF_ENV = DISABLE_NLS="$(DISABLE_NLS)"

MINIDLNA_CONF_OPT = --enable-tivo \
	--with-os-name=Alt-F \
	--with-os-version=0.1RC3 \
	--with-os-url=http://code.google.com/p/alt-f \
	--program-prefix=""

$(eval $(call AUTOTARGETS,package/multimedia,minidlna))

$(MINIDLNA_HOOK_POST_CONFIGURE):
	sed -i 's|^#define USE_DAEMON.*|/* & */|' $(MINIDLNA_DIR)/config.h
	touch $@

$(MINIDLNA_HOOK_POST_INSTALL):
	mv $(TARGET_DIR)/usr/sbin/minidlnad $(TARGET_DIR)/usr/sbin/minidlna 
	touch $@