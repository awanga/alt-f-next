#############################################################
#
# libgd
#
#############################################################

LIBGD_VERSION:=2.0.33
LIBGD_SITE:=https://bitbucket.org/pierrejoye/gd-libgd/get
LIBGD_SOURCE=GD_$(subst .,_,$(LIBGD_VERSION)).tar.bz2
LIBGD_LIBTOOL_PATCH = NO
LIBGD_INSTALL_STAGING = YES
LIBGD_SUBDIR = src

LIBGD_CONF_OPT = --disable-rpath

$(eval $(call AUTOTARGETS,package,libgd))

$(LIBGD_HOOK_POST_CONFIGURE):
	sed -i 's|^CPPFLAGS.*||' $(LIBGD_DIR)/$(LIBGD_SUBDIR)/Makefile
	touch $@