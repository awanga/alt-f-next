#############################################################
#
# libgd
#
#############################################################

# new orphan, "flying around", version
#LIBGD_VERSION:=2.0.35
#LIBGD_SITE:=http://google-desktop-for-linux-mirror.googlecode.com/files
#or http://www.chipsnbytes.net/downloads/gd-2.0.35.tar.gz
#or http://www.2let.at/gd-2.0.35.tar.gz
#LIBGD_SOURCE=gd-$(LIBGD_VERSION).tar.gz
#LIBGD_SUBDIR = $(LIBGD_VERSION)

#old, original author version
LIBGD_VERSION:=2.0.33
LIBGD_SITE:=https://bitbucket.org/pierrejoye/gd-libgd/get
LIBGD_SOURCE=GD_$(subst .,_,$(LIBGD_VERSION)).tar.bz2
LIBGD_SUBDIR = src

LIBGD_LIBTOOL_PATCH = NO
LIBGD_INSTALL_STAGING = YES

LIBGD_CONF_OPT = --disable-rpath --without-freetype --without-fontconfig --without-xpm

$(eval $(call AUTOTARGETS,package,libgd))

# configure leak, CPPFLAGS points to /usr/include, remove it
$(LIBGD_HOOK_POST_CONFIGURE):
	sed -i 's|^CPPFLAGS.*||' $(LIBGD_DIR)/$(LIBGD_SUBDIR)/Makefile
	touch $@

$(LIBGD_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/gdlib-config
	touch $@