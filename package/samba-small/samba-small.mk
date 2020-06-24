################################################################################
#
# samba-small
#
################################################################################

SAMBA_SMALL_VERSION = 4.10.17
SAMBA_SMALL_SITE = https://download.samba.org/pub/samba/stable
SAMBA_SMALL_SOURCE = samba-$(SAMBA_SMALL_VERSION).tar.gz
SAMBA_SMALL_INSTALL_STAGING = YES
SAMBA_SMALL_LICENSE = GPL-3.0+
SAMBA_SMALL_LICENSE_FILES = COPYING
SAMBA_SMALL_DEPENDENCIES = \
	host-e2fsprogs host-heimdal host-nfs-utils \
	popt zlib \

SAMBA_SMALL_CONF_ENV = \
	XSLTPROC=false \
	WAF_NO_PREFORK=1

SAMBA_SMALL_CONF_OPTS += \
	--with-static-modules=!FORCED \
	--with-shared-modules=LEASES_DB,LEASES_UTIL,LIBCLI_AUTH,LIBTSOCKET,LOCKING,NDR_IOCTL,NDR_QUOTA,NDR_SECURITY,NDR_SRVSVC,NDR_SVCCTL,PROFILE,RPC_NDR_SRVSVC,!FORCED \
	--disable-avahi \
	--disable-cephfs \
	--disable-cups \
	--disable-gnutls \
	--disable-python \
	--without-ad-dc \
	--without-ads \
	--without-fam \
	--without-gettext \
	--without-gpgme \
	--without-json \
	--without-libarchive \
	--without-ldap \
	--without-lttng \
	--without-ntvfs-fileserver \
	--without-systemd \
	--without-winbind \
	--nopyc --nopyo

ifeq ($(BR2_PACKAGE_LIBTIRPC),y)
SAMBA_SMALL_CFLAGS += `$(PKG_CONFIG_HOST_BINARY) --cflags libtirpc`
SAMBA_SMALL_LDFLAGS += `$(PKG_CONFIG_HOST_BINARY) --libs libtirpc`
SAMBA_SMALL_DEPENDENCIES += libtirpc host-pkgconf
endif

ifeq ($(BR2_PACKAGE_ACL),y)
SAMBA_SMALL_CONF_OPTS += --with-acl-support
SAMBA_SMALL_DEPENDENCIES += acl
else
SAMBA_SMALL_CONF_OPTS += --without-acl-support
endif

SAMBA_SMALL_CONF_OPTS += --without-regedit

# The ctdb tests (cluster) need bash and take up some space
# They're normally intended for debugging so remove them
define SAMBA_SMALL_REMOVE_CTDB_TESTS
	rm -rf $(TARGET_DIR)/usr/lib/ctdb-tests
	rm -rf $(TARGET_DIR)/usr/share/ctdb-tests
	rm -f $(TARGET_DIR)/usr/bin/ctdb_run_*tests
endef
SAMBA_SMALL_POST_INSTALL_TARGET_HOOKS += SAMBA_SMALL_REMOVE_CTDB_TESTS

SAMBA_SMALL_CFLAGS += -Os -fdata-sections -ffunction-sections

SAMBA_SMALL_LDFLAGS += -Wl,--gc-sections
ifeq ($(BR2_BINUTILS_ENABLE_LTO),y)
SAMBA_SMALL_LDFLAGS += -flto
endif

ifeq ($(BR2_TOOLCHAIN_BUILDROOT_MUSL),y)
SAMBA_SMALL_CFLAGS += -DNETDB_INTERNAL=(-1) -DNETDB_SUCCESS=(0)
endif

define SAMBA_SMALL_CONFIGURE_CMDS
	cp package/samba-small/samba4-cache.txt $(@D)/cache.txt;
	echo 'Checking uname machine type: $(BR2_ARCH)' >>$(@D)/cache.txt;
	(cd $(@D); \
		$(TARGET_CONFIGURE_OPTS) \
		CFLAGS="$(TARGET_CFLAGS) $(SAMBA_SMALL_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS) $(SAMBA_SMALL_LDFLAGS)" \
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
			--disable-rpath-private-install \
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
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) small_samba
endef

#define SAMBA_SMALL_INSTALL_STAGING_CMDS
#	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(STAGING_DIR) install-small_samba
#endef

define SAMBA_SMALL_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) install-small_samba
endef

define SAMBA_SMALL_REMOVE_EXTRAS
	rm -f $(TARGET_DIR)/usr/bin/pidl
	rm -f $(TARGET_DIR)/usr/bin/smbtorture
	rm -fR $(TARGET_DIR)/usr/include/samba
	rm -fR $(TARGET_DIR)/usr/lib/python2.7/site-packages/samba
	rm -fR $(TARGET_DIR)/usr/share/perl5/Parse
endef

SAMBA_SMALL_POST_INSTALL_TARGET_HOOKS += SAMBA_SMALL_REMOVE_EXTRAS

$(eval $(generic-package))
