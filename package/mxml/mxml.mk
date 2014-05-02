#############################################################
#
# mxml
#
#############################################################

MXML_VERSION:=2.6
# author site? http://www.msweet.org/files/project3/mxml-2.6.tar.gz
MXML_SITE = $(BR2_DEBIAN_MIRROR)/debian/pool/main/m/mxml
MXML_SOURCE = mxml_$(MXML_VERSION).orig.tar.gz
MXML_DIR=$(BUILD_DIR)/mxml-$(MXML_VERSION)

MXML_LIBTOOL_PATCH = NO
MXML_INSTALL_STAGING = YES
MXML_INSTALL_TARGET = YES

MXML_CONF_OPT = --disable-static --enable-shared

$(eval $(call AUTOTARGETS,package,mxml))
