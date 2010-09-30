#############################################################
#
# openssh
#
#############################################################
OPENSSH_VERSION=5.1p1
OPENSSH_SITE=ftp://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable
OPENSSH_CONF_ENV = LD=$(TARGET_CC)
OPENSSH_CONF_OPT = --libexecdir=/usr/lib --disable-lastlog --disable-utmp \
		--disable-utmpx --disable-wtmp --disable-wtmpx --without-x
OPENSSH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
OPENSSH_DEPENDENCIES = zlib openssl

$(eval $(call AUTOTARGETS,package,openssh))

ifneq ($(BR2_PACKAGE_OPENSSH_SFTP_ONLY),y)

$(OPENSSH_HOOK_POST_INSTALL):
	$(INSTALL) -D -m 755 package/openssh/S50sshd $(TARGET_DIR)/etc/init.d/S50sshd
	touch $@

else

# this is a hack. Use AUTOTARGETS to do everything but install.
# At the build end, the post build hook runs, which installs just sftp-server
# and touchs the autotools dir as if a target install had been run.
# dont touch the dependency, otherwise a full install occurs.
$(OPENSSH_HOOK_POST_BUILD):
	$(INSTALL) -m 0755 $(OPENSSH_DIR)/sftp-server $(TARGET_DIR)/usr/libexec
	touch $(PROJECT_BUILD_DIR)/autotools-stamps/openssh_target_installed
#	touch $@ # dont! and don't remove me!

endif
