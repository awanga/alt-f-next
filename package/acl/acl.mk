#############################################################
#
# acl
#
#############################################################
ACL_VERSION:=2.2.52
ACL_SOURCE:=acl-$(ACL_VERSION).src.tar.gz
ACL_SITE:=http://download.savannah.gnu.org/releases/acl

ACL_INSTALL_STAGING = YES
ACL_LIBTOOL_PATCH = NO
ACL_DEPENDENCIES = uclibc attr libintl
ACL_DEPENDENCIES_HOST = attr-host
ACL_CONF_OPT = --disable-gettext
ACL_CONF_ENV = LDFLAGS=-lintl
ACL_INSTALL_STAGING=YES

ACL_INSTALL_STAGING_OPT = DESTDIR="$(STAGING_DIR)" install install-dev install-lib
ACL_HOST_INSTALL_OPT = DESTDIR="$(HOST_DIR)" install install-dev install-lib
ACL_INSTALL_TARGET_OPT = DESTDIR="$(TARGET_DIR)" install install-lib

$(eval $(call AUTOTARGETS,package,acl))
$(eval $(call AUTOTARGETS_HOST,package,acl))
