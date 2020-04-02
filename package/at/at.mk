#############################################################
#
# at
#
#############################################################

AT_VERSION:=3.1.23
AT_SOURCE:=at_$(AT_VERSION).orig.tar.gz
AT_SITE:=$(BR2_DEBIAN_MIRROR)/debian/pool/main/a/at

AT_DIR:=$(BUILD_DIR)/at-$(AT_VERSION)
AT_CAT:=$(ZCAT)
AT_TARGET_SCRIPT:=etc/init.d/S27at
AT_BINARY:=at

$(DL_DIR)/$(AT_SOURCE):
	 $(call DOWNLOAD,$(AT_SITE),$(AT_SOURCE))

at-source: $(DL_DIR)/$(AT_SOURCE)

$(AT_DIR)/.unpacked: $(DL_DIR)/$(AT_SOURCE)
	$(AT_CAT) $(DL_DIR)/$(AT_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(AT_DIR) package/at/ at\*.patch
	touch $@

$(AT_DIR)/.configured: $(AT_DIR)/.unpacked
	(cd $(AT_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		SENDMAIL=/usr/sbin/sendmail \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--libdir=/lib \
		--libexecdir=/usr/lib \
		--sysconfdir=/etc \
		--localstatedir=/var \
		--with-jobdir=/var/spool/atjobs \
		--with-atspool=/var/spool/atspool \
		--with-daemon_username=at \
		--with-daemon_groupname=at \
	)
	$(SED) 's|$$(INSTALL) -g $$(DAEMON_GROUPNAME) -o $$(DAEMON_USERNAME)|$$(INSTALL) -g 8 -o 5|' \
		-e 's|chown $$(DAEMON_USERNAME):$$(DAEMON_GROUPNAME)|chown 5:8|' \
		-e 's|$$(INSTALL) -o root -g $$(DAEMON_GROUPNAME)|$$(INSTALL) -o root -g 8|' \
		$(AT_DIR)/Makefile
	touch $@

$(AT_DIR)/$(AT_BINARY): $(AT_DIR)/.configured
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(AT_DIR)
	touch $@

$(TARGET_DIR)/$(AT_TARGET_SCRIPT): $(AT_DIR)/$(AT_BINARY)
	# Use fakeroot to pretend to do 'make install' as root
	echo '$(MAKE) DAEMON_USERNAME=at DAEMON_GROUPNAME=at ' \
	 '$(TARGET_CONFIGURE_OPTS) DESTDIR=$(TARGET_DIR) -C $(AT_DIR) install' \
		> $(PROJECT_BUILD_DIR)/.fakeroot.at
ifneq ($(BR2_HAVE_MANPAGES),y)
	echo 'rm -rf $(TARGET_DIR)/usr/man' >> $(PROJECT_BUILD_DIR)/.fakeroot.at
endif
	echo 'rm -rf $(TARGET_DIR)/usr/doc' >> $(PROJECT_BUILD_DIR)/.fakeroot.at
	echo 'rm -rf $(TARGET_DIR)/var/lib/at*' >> $(PROJECT_BUILD_DIR)/.fakeroot.at
	echo 'rm -rf $(TARGET_DIR)/var/spool' >> $(PROJECT_BUILD_DIR)/.fakeroot.at
	echo '$(TARGET_STRIP) $(TARGET_DIR)/usr/sbin/atd $(TARGET_DIR)/usr/bin/at' >> $(PROJECT_BUILD_DIR)/.fakeroot.at

at: uclibc host-fakeroot msmtp $(TARGET_DIR)/$(AT_TARGET_SCRIPT)

at-configure: $(AT_DIR)/.configured

at-build: $(AT_DIR)/$(AT_BINARY)

at-clean:
	-$(MAKE) DESTDIR=$(TARGET_DIR) CC=$(TARGET_CC) -C $(AT_DIR) uninstall
	rm -f $(TARGET_DIR)/$(AT_TARGET_SCRIPT) $(TARGET_DIR)/etc/init.d/S99at
	-$(MAKE) -C $(AT_DIR) clean

at-dirclean:
	rm -rf $(AT_DIR)

.PHONY: at
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_AT),y)
TARGETS+=at
endif
