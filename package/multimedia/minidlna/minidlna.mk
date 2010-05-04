#############################################################
#
# minidlna
#
#############################################################
MINIDLNA_VERSION = 230410
MINIDLNA_SOURCE = minidlna-cvs-$(MINIDLNA_VERSION).tgz
MINIDLNA_SITE = http://sourceforge.net/projects/minidlna/develop
MINIDLNA_AUTORECONF = NO
MINIDLNA_INSTALL_STAGING = NO
MINIDLNA_INSTALL_TARGET = YES
MINIDLNA_LIBTOOL_PATCH = NO
	
MINIDLNA_DEPENDENCIES = uclibc libexif jpeg libid3tag flac libvorbis sqlite ffmpeg

$(eval $(call AUTOTARGETS,package/multimedia,minidlna))
	
$(MINIDLNA_HOOK_POST_EXTRACT):
	touch $(MINIDLNA_DIR)/configure
	chmod +x $(MINIDLNA_DIR)/configure
	touch $@
