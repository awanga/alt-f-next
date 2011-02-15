#############################################################
#
# jpeg (libraries needed by some apps)
#
#############################################################

JPEG_VERSION:=8c
JPEG_DIR=$(BUILD_DIR)/jpeg-$(JPEG_VERSION)
JPEG_SITE:=http://www.ijg.org/files/
JPEG_SOURCE=jpegsrc.v$(JPEG_VERSION).tar.gz
JPEG_LIBTOOL_PATCH = NO
JPEG_INSTALL_STAGING = YES

JPEG_CONF_OPT = --disable-static --program-prefix=""

$(eval $(call AUTOTARGETS,package,jpeg))