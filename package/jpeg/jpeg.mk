#############################################################
#
# jpeg (libraries needed by some apps)
#
#############################################################

JPEG_VERSION:=8c
JPEG_SITE:=http://www.ijg.org/files/
JPEG_SOURCE=jpegsrc.v$(JPEG_VERSION).tar.gz

JPEG_DIR=$(BUILD_DIR)/jpeg-$(JPEG_VERSION)

JPEG_LIBTOOL_PATCH = NO
JPEG_INSTALL_STAGING = YES

JPEG_PROGS = cjpeg djpeg jpegtran rdjpgcom wrjpgcom 

JPEG_CONF_OPT = --disable-static --program-prefix=""

$(eval $(call AUTOTARGETS,package,jpeg))

$(JPEG_HOOK_POST_INSTALL):
ifneq ($(BR2_PACKAGE_JPEG_PROGS),y)
	(cd $(TARGET_DIR)/usr/bin; rm -f $(JPEG_PROGS))
endif
	touch $@