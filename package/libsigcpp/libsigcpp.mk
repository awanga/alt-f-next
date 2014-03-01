#############################################################
#
# libsigcpp
#
#############################################################

LIBSIGCPP_VERSION_MAJOR = 2.2
LIBSIGCPP_VERSION_MINOR = 10
LIBSIGCPP_VERSION = 2.2.10
#LIBSIGCPP_VERSION = $(LIBSIGCPP_VERSION_MAJOR).$(LIBSIGCPP_VERSION_MINOR) # mkpkg.sh complains
LIBSIGCPP_SOURCE = libsigc++-$(LIBSIGCPP_VERSION).tar.bz2
LIBSIGCPP_SITE = http://ftp.gnome.org/pub/GNOME/sources/libsigc++/$(LIBSIGCPP_VERSION_MAJOR)
LIBSIGCPP_AUTORECONF = NO
LIBSIGCPP_INSTALL_STAGING = YES
LIBSIGCPP_INSTALL_TARGET = YES
LIBSIGCPP_LIBTOOL_PATCH = NO
LIBSIGCPP_CONF_OPT = --disable-documentation
LIBSIGCPP_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS,package,libsigcpp))

$(LIBSIGCPP_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/lib/sigc++-2.0
	cp $(STAGING_DIR)/usr/lib/sigc++-2.0/include/sigc++config.h \
		$(STAGING_DIR)/usr/include
	ln -s $(STAGING_DIR)/usr/include/sigc++-2.0/sigc++ \
		$(STAGING_DIR)/usr/include/sigc++
	touch $@

