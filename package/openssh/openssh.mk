#############################################################
#
# openssh
#
#############################################################

#OPENSSH_VERSION=7.1p2
OPENSSH_VERSION=8.1p1

OPENSSH_SITE=https://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable

OPENSSH_CONF_ENV = LD=$(TARGET_CC)
OPENSSH_CONF_OPT = --sysconfdir=/etc/ssh --with-privsep-path=/var/run/vsftpd \
	--disable-lastlog --disable-utmp --disable-utmpx --disable-wtmp --disable-wtmpx \
	--without-ssl-engine --without-pam --without-selinux --with-md5-passwords

OPENSSH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

OPENSSH_SFTP_STAMP = $(PROJECT_BUILD_DIR)/autotools-stamps/openssh-sftp_target_installed

OPENSSH_DEPENDENCIES = zlib openssl

$(eval $(call AUTOTARGETS,package,openssh))

# is there other way? Use AUTOTARGETS to do everything but install.
# At the build end, the post build hook runs, which installs just sftp-server

ifneq ($(BR2_PACKAGE_OPENSSH_SFTP),y)

$(OPENSSH_HOOK_POST_INSTALL):
	#sed -i 's/#.*Ciphers /Ciphers aes128-cbc,/' $(TARGET_DIR)/etc/ssh/ssh_config
	sed -i -e '/Subsystem/s/libexec/lib/' \
		-e 's/#PermitRootLogin.*$$/PermitRootLogin yes/' \
		-e 's/#PasswordAuthentication/PasswordAuthentication/' \
		$(TARGET_DIR)/etc/ssh/sshd_config
	mv $(TARGET_DIR)/usr/bin/ssh $(TARGET_DIR)/usr/bin/ssh-openssh
	mv $(TARGET_DIR)/usr/bin/scp $(TARGET_DIR)/usr/bin/scp-openssh
	touch $@

else

$(OPENSSH_TARGET_INSTALL_TARGET) $(OPENSSH_SFTP_STAMP):
	$(INSTALL) -m 0755 $(OPENSSH_DIR)/sftp-server $(TARGET_DIR)/usr/lib
	touch $@ $(OPENSSH_SFTP_STAMP)

endif
