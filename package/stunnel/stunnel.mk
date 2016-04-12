#############################################################
#
# stunnel
#
#############################################################

STUNNEL_VERSION:=5.30
STUNNEL_SITE:=http://www.usenix.org.uk/mirrors/stunnel/archive/5.x

STUNNEL_SOURCE:=stunnel-$(STUNNEL_VERSION).tar.gz
STUNNEL_CAT:=$(ZCAT)
STUNNEL_DIR:=$(BUILD_DIR)/stunnel-$(STUNNEL_VERSION)
STUNNEL_LIBTOOL_PATCH = NO
STUNNEL_DEPENDENCIES := uclibc openssl

$(DL_DIR)/$(STUNNEL_SOURCE):
	 $(call DOWNLOAD,$(STUNNEL_SITE),$(STUNNEL_SOURCE))

stunnel-source: $(DL_DIR)/$(STUNNEL_SOURCE)

$(STUNNEL_DIR)/.unpacked: $(DL_DIR)/$(STUNNEL_SOURCE)
	$(STUNNEL_CAT) $(DL_DIR)/$(STUNNEL_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	$(CONFIG_UPDATE) $(STUNNEL_DIR)
	toolchain/patch-kernel.sh $(STUNNEL_DIR) package/stunnel stunnel\*.patch
	touch $(STUNNEL_DIR)/.unpacked

$(STUNNEL_DIR)/.configured: $(STUNNEL_DIR)/.unpacked
	(cd $(STUNNEL_DIR); rm -rf config.cache; \
		ax_cv_check_cflags___fstack_protector=no \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--bindir=/usr/bin \
		--sbindir=/usr/sbin \
		--libdir=/lib \
		--libexecdir=/usr/lib \
		--sysconfdir=/etc \
		--datadir=/usr/share \
		--localstatedir=/var \
		--mandir=/usr/man \
		--infodir=/usr/info \
		--with-random=/dev/urandom \
		--with-threads=fork \
		--disable-libwrap \
		--disable-systemd \
		--with-ssl=$(STAGING_DIR)/usr/ \
		--disable-fips \
		$(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
	)
	sed -i -e 's|.*HAVE_DEV_PTMX.*|#define HAVE_DEV_PTMX 1|' \
		-e 's|.*HAVE_DAEMON.*|/\* #undef HAVE_DAEMON \*/|' \
		$(STUNNEL_DIR)/src/config.h
	touch $(STUNNEL_DIR)/.configured

$(STUNNEL_DIR)/src/stunnel: $(STUNNEL_DIR)/.configured
	$(MAKE) CC=$(TARGET_CC) CFLAGS="$(TARGET_CFLAGS) -fPIE" -C $(STUNNEL_DIR)

$(TARGET_DIR)/usr/bin/stunnel: $(STUNNEL_DIR)/src/stunnel
	install -c $(STUNNEL_DIR)/src/stunnel $(TARGET_DIR)/usr/bin/stunnel
	$(STRIPCMD) $(TARGET_DIR)/usr/bin/stunnel > /dev/null 2>&1
ifeq ($(BR2_CROSS_TOOLCHAIN_TARGET_UTILS),y)
	mkdir -p $(STAGING_DIR)/usr/$(REAL_GNU_TARGET_NAME)/target_utils
	install -c $(TARGET_DIR)/usr/bin/stunnel \
		$(STAGING_DIR)/usr/$(REAL_GNU_TARGET_NAME)/target_utils/stunnel
endif

stunnel-configure: $(STUNNEL_DIR)/.configured

stunnel-build: $(STUNNEL_DIR)/src/stunnel

stunnel: uclibc $(TARGET_DIR)/usr/bin/stunnel

stunnel-clean:
	-$(MAKE) -C $(STUNNEL_DIR) clean
	rm -f $(TARGET_DIR)/usr/bin/stunnel

stunnel-dirclean:
	rm -rf $(STUNNEL_DIR)


#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_STUNNEL),y)
TARGETS+=stunnel
endif
