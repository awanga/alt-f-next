################################################################################
#
# samba-small
#
################################################################################

SAMBA_SMALL_VERSION = 4.6.7
SAMBA_SMALL_SITE = https://download.samba.org/pub/samba/stable
SAMBA_SMALL_SOURCE = samba-$(SAMBA_SMALL_VERSION).tar.gz
SAMBA_SMALL_INSTALL_STAGING = YES
SAMBA_SMALL_LICENSE = GPL-3.0+
SAMBA_SMALL_LICENSE_FILES = COPYING
SAMBA_SMALL_DEPENDENCIES = \
	host-e2fsprogs host-heimdal host-python \
	micropython zlib

SAMBA_SMALL_CONF_OPTS +=	--with-static-modules=ALL --nonshared-binary=ALL \
				--without-acl-support \
				--disable-cups \
				--disable-avahi \
				--without-fam \
				--disable-gnutls \
				--without-regedit \
				--without-ad-dc \
				--disable-cephfs \
				--without-systemd \
				--without-lttng \
				--without-ads --without-ldap \
				--without-gpgme \
				--without-ntvfs-fileserver \
				--nopyc --nopyo

ifeq ($(BR2_PACKAGE_POPT),y)
SAMBA_SMALL_DEPENDENCIES += popt
endif

ifeq ($(BR2_PACKAGE_GETTEXT),y)
SAMBA_SMALL_DEPENDENCIES += gettext
else
SAMBA_SMALL_CONF_OPTS += --without-gettext
endif

# The ctdb tests (cluster) need bash and take up some space
# They're normally intended for debugging so remove them
define SAMBA_SMALL_REMOVE_CTDB_TESTS
	rm -rf $(TARGET_DIR)/usr/lib/ctdb-tests
	rm -rf $(TARGET_DIR)/usr/share/ctdb-tests
	rm -f $(TARGET_DIR)/usr/bin/ctdb_run_*tests
endef
SAMBA_SMALL_POST_INSTALL_TARGET_HOOKS += SAMBA_SMALL_REMOVE_CTDB_TESTS

SAMBA_SMALL_CONF_ENV += CFLAGS="$(TARGET_CFLAGS) -Os -fdata-sections -ffunction-sections"
ifeq ($(BR2_BINUTILS_ENABLE_LTO),y)
SAMBA_SMALL_CONF_ENV += LDFLAGS="$(TARGET_LDFLAGS) -flto -Wl,--gc-sections"
else
SAMBA_SMALL_CONF_ENV += LDFLAGS="$(TARGET_LDFLAGS) -Wl,--gc-sections"
endif

define SAMBA_SMALL_CONFIGURE_CMDS
	cp package/samba-small/samba4-cache.txt $(@D)/cache.txt;
	echo 'Checking uname machine type: $(BR2_ARCH)' >>$(@D)/cache.txt;
	(cd $(@D); \
		PYTHON_CONFIG="$(STAGING_DIR)/usr/bin/python-config" \
		python_LDFLAGS="" \
		python_LIBDIR="" \
		$(TARGET_CONFIGURE_OPTS) \
		$(SAMBA_SMALL_CONF_ENV) \
		./buildtools/bin/waf configure \
			--prefix=/usr \
			--sysconfdir=/etc \
			--localstatedir=/var \
			--with-libiconv=$(STAGING_DIR)/usr \
			--enable-fhs \
			--cross-compile \
			--cross-answers=$(@D)/cache.txt \
			--hostcc=gcc \
			--disable-rpath \
			--disable-rpath-install \
			--disable-iprint \
			--without-pam \
			--without-dmapi \
			--disable-glusterfs \
			--without-cluster-support \
			--bundled-libraries='!asn1_compile,!compile_et' \
			$(SAMBA_SMALL_CONF_OPTS) \
	)
endef

define SAMBA_SMALL_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define SAMBA_SMALL_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(STAGING_DIR) install
endef

define SAMBA_SMALL_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) install
endef

define SAMBA_SMALL_REMOVE_SMBTORTURE
	rm -f $(TARGET_DIR)/usr/bin/smbtorture
endef

define SAMBA_SMALL_MULTICALL_LINKS
	ln -sf samba_multicall $(TARGET_DIR)/usr/sbin/smbd
	ln -sf samba_multicall $(TARGET_DIR)/usr/sbin/nmbd
	ln -sf ../sbin/samba_multicall $(TARGET_DIR)/usr/bin/smbpasswd
	ln -sf ../sbin/samba_multicall $(TARGET_DIR)/usr/bin/smbstatus
	ln -sf ../sbin/samba_multicall $(TARGET_DIR)/usr/bin/smbtree
endef

SAMBA_SMALL_POST_INSTALL_TARGET_HOOKS += SAMBA_SMALL_REMOVE_SMBTORTURE
SAMBA_SMALL_POST_INSTALL_TARGET_HOOKS += SAMBA_SMALL_MULTICALL_LINKS

$(eval $(generic-package))
