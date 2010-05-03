#############################################################
#
# host-pkgconfig
#
#############################################################
HOST_PKGCONFIG_VERSION = 0.23
HOST_PKGCONFIG_SOURCE = pkg-config-$(HOST_PKGCONFIG_VERSION).tar.gz
HOST_PKGCONFIG_SITE = http://pkgconfig.freedesktop.org/releases/

# pkg-config for the host
HOST_PKGCONFIG_DIR:=$(BUILD_DIR)/pkg-config-$(HOST_PKGCONFIG_VERSION)-host
HOST_PKGCONFIG_HOST_BINARY:=$(HOST_DIR)/usr/bin/pkg-config

$(DL_DIR)/$(HOST_PKGCONFIG_SOURCE):
	$(call DOWNLOAD,$(HOST_PKGCONFIG_SITE),$(HOST_PKGCONFIG_SOURCE))

$(HOST_PKGCONFIG_DIR)/.unpacked: $(DL_DIR)/$(HOST_PKGCONFIG_SOURCE)
	mkdir -p $(HOST_PKGCONFIG_DIR)
	$(INFLATE$(suffix $(HOST_PKGCONFIG_SOURCE))) $< | \
		$(TAR) $(TAR_STRIP_COMPONENTS)=1 -C $(HOST_PKGCONFIG_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(HOST_PKGCONFIG_DIR) package/pkg-config/ \*.patch
	touch $@

$(HOST_PKGCONFIG_DIR)/.configured: $(HOST_PKGCONFIG_DIR)/.unpacked
	(cd $(HOST_PKGCONFIG_DIR); rm -rf config.cache; \
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

$(HOST_PKGCONFIG_DIR)/.compiled: $(HOST_PKGCONFIG_DIR)/.configured
	$(MAKE) -C $(HOST_PKGCONFIG_DIR)
	touch $@

$(HOST_PKGCONFIG_DIR)/.installed: $(HOST_PKGCONFIG_DIR)/.compiled
	$(MAKE) -C $(HOST_PKGCONFIG_DIR) install
	install -D -m 0644 $(HOST_DIR)/usr/share/aclocal/pkg.m4 \
		$(STAGING_DIR)/usr/share/aclocal/pkg.m4
	touch $@

host-pkgconfig: $(HOST_PKGCONFIG_DIR)/.installed

host-pkgconfig-source: $(HOST_PKGCONFIG_DIR)/.unpacked

host-pkgconfig-clean:
	rm -f $(addprefix $(HOST_PKGCONFIG_DIR)/host_pkgconfig_,unpacked configured compiled installed)
	-$(MAKE) -C $(HOST_PKGCONFIG_DIR) uninstall
	-$(MAKE) -C $(HOST_PKGCONFIG_DIR) clean

host-pkgconfig-dirclean:
	rm -rf $(HOST_PKGCONFIG_DIR)

ifeq ($(BR2_PACKAGE_HOST_PKGCONFIG),y)
TARGETS+=host-pkgconfig
endif
