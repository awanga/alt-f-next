#############################################################
#
# mxml
#
#############################################################

MXML_VERSION:=2.6
MXML_DIR=$(BUILD_DIR)/mxml-$(MXML_VERSION)
MXML_SITE = http://ftp.easysw.com/pub/mxml/$(MXML_VERSION)
MXML_SOURCE = mxml-$(MXML_VERSION).tar.gz
MXML_LIBTOOL_PATCH = NO
MXML_INSTALL_STAGING = YES
MXML_INSTALL_TARGET = YES

MXML_CONF_OPT = --disable-static --enable-shared

$(eval $(call AUTOTARGETS,package,mxml))