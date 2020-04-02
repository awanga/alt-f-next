#############################################################
#
# attr
#
#############################################################
ATTR_VERSION:=2.4.47
ATTR_SOURCE:=attr-$(ATTR_VERSION).src.tar.gz
ATTR_SITE:=http://download.savannah.nongnu.org/releases/attr
ATTR_LIBTOOL_PATCH = NO
ATTR_INSTALL_STAGING=YES

ATTR_INSTALL_STAGING_OPT = DESTDIR="$(STAGING_DIR)" install install-dev install-lib
ATTR_INSTALL_TARGET_OPT = DESTDIR="$(TARGET_DIR)" install install-lib
ATTR_HOST_INSTALL_OPT = DESTDIR="$(HOST_DIR)" install install-dev install-lib

ATTR_CONF_OPT = --disable-gettext

$(eval $(call AUTOTARGETS,package,attr))
$(eval $(call AUTOTARGETS_HOST,package,attr))
