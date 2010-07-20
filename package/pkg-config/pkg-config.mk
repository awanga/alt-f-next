#############################################################
#
# pkgconfig
#
#############################################################
PKG_CONFIG_VERSION = 0.23
PKG_CONFIG_SOURCE = pkg-config-$(PKG_CONFIG_VERSION).tar.gz
PKG_CONFIG_SITE = http://pkgconfig.freedesktop.org/releases/

# this is a mess. I want a host only pkg-config, so I will add 
# a package just for that purpose.

# but if I really wanted a target pkg-config, I would need to
# install the glib2 package, as the pkg-config included glib12
# does not compile (but buildroot glib12 package is fine)

PKG_CONFIG_TARGET = no

ifeq ($(BR2_ENABLE_DEBUG),y) # install-exec doesn't install aclocal stuff
PKG_CONFIG_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
endif

ifeq ($(PKG_CONFIG_TARGET),yes)  # jc: install for the target also
#PKG_CONFIG_DEPENDENCIES = uclibc libglib2 
# glib2 is a nonsense, but with included glib12 it does not work
# perhaps depending on glib12?
PKG_CONFIG_DEPENDENCIES = uclibc
PKG_CONFIG_CONF_OPT = --with-installed-glib # means: Use installed Glib-2.x
$(eval $(call AUTOTARGETS,package,pkg-config))
endif

# pkg-config for the host
PKG_CONFIG_HOST_DIR:=$(BUILD_DIR)/pkg-config-$(PKG_CONFIG_VERSION)-host
PKG_CONFIG_HOST_BINARY:=$(HOST_DIR)/usr/bin/pkg-config

# comment, interfere with host-pkgconfig
#$(DL_DIR)/$(PKG_CONFIG_SOURCE):
#	$(call DOWNLOAD,$(PKG_CONFIG_SITE),$(PKG_CONFIG_SOURCE))

$(STAMP_DIR)/host_pkgconfig_unpacked: $(DL_DIR)/$(PKG_CONFIG_SOURCE)
	mkdir -p $(PKG_CONFIG_HOST_DIR)
	$(INFLATE$(suffix $(PKG_CONFIG_SOURCE))) $< | \
		$(TAR) $(TAR_STRIP_COMPONENTS)=1 -C $(PKG_CONFIG_HOST_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(PKG_CONFIG_HOST_DIR) package/pkg-config/ \*.patch
	touch $@

$(STAMP_DIR)/host_pkgconfig_configured: $(STAMP_DIR)/host_pkgconfig_unpacked
	(cd $(PKG_CONFIG_HOST_DIR); rm -rf config.cache; \
		$(HOST_CONFIGURE_OPTS) \
		CFLAGS="$(HOST_CFLAGS)" \
		LDFLAGS="$(HOST_LDFLAGS)" \
		./configure \
		--prefix="$(HOST_DIR)/usr" \
		--sysconfdir="$(HOST_DIR)/etc" \
		--with-pc-path="$(STAGING_DIR)/usr/lib/pkgconfig" \
		--disable-static \
	)
	touch $@

$(STAMP_DIR)/host_pkgconfig_compiled: $(STAMP_DIR)/host_pkgconfig_configured
	$(MAKE) -C $(PKG_CONFIG_HOST_DIR)
	touch $@

$(STAMP_DIR)/host_pkgconfig_installed: $(STAMP_DIR)/host_pkgconfig_compiled
	$(MAKE) -C $(PKG_CONFIG_HOST_DIR) install
	install -D -m 0644 $(HOST_DIR)/usr/share/aclocal/pkg.m4 \
		$(STAGING_DIR)/usr/share/aclocal/pkg.m4
	touch $@

# "commented" interfere with host-pkgconfig
xxxhost-pkgconfig: $(STAMP_DIR)/host_pkgconfig_installed

# "commented" interfere with host-pkgconfig
xxxhost-pkgconfig-clean:
	rm -f $(addprefix $(STAMP_DIR)/host_pkgconfig_,unpacked configured compiled installed)
	-$(MAKE) -C $(PKG_CONFIG_HOST_DIR) uninstall
	-$(MAKE) -C $(PKG_CONFIG_HOST_DIR) clean

# "commented" interfere with host-pkgconfig
xxxhost-pkgconfig-dirclean:
	rm -rf $(PKG_CONFIG_HOST_DIR)
