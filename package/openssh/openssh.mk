#############################################################
#
# openssh
#
#############################################################

#OPENSSH_VERSION=6.9p1
OPENSSH_VERSION=7.1p2

OPENSSH_SITE=ftp://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable

OPENSSH_CONF_ENV = LD=$(TARGET_CC)
OPENSSH_CONF_OPT = --sysconfdir=/etc/ssh --with-privsep-path=/var/run/vsftpd \
	-disable-lastlog --disable-utmp --disable-utmpx --disable-wtmp --disable-wtmpx

OPENSSH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

OPENSSH_SFTP_STAMP = $(PROJECT_BUILD_DIR)/autotools-stamps/openssh-sftp_target_installed

# The bellow dependency on dropbear is a fake. Dropbear installs ssh and scp as a link
# to dropbear, so if it is installed after openssh it will override those binaries

OPENSSH_DEPENDENCIES = zlib openssl dropbear

$(eval $(call AUTOTARGETS,package,openssh))

# this is a hack. Use AUTOTARGETS to do everything but install.
# At the build end, the post build hook runs, which installs just sftp-server

ifneq ($(BR2_PACKAGE_OPENSSH_SFTP),y)

$(OPENSSH_HOOK_POST_INSTALL):
	sed -i 's/#.*Ciphers /Ciphers aes128-cbc,/' $(TARGET_DIR)/etc/ssh/ssh_config
	sed -i -e '/Subsystem/s/libexec/lib/' \
		-e 's/#PermitRootLogin no/PermitRootLogin yes/' \
		$(TARGET_DIR)/etc/ssh/sshd_config
	touch $@

else

$(OPENSSH_TARGET_INSTALL_TARGET) $(OPENSSH_SFTP_STAMP):
	$(INSTALL) -m 0755 $(OPENSSH_DIR)/sftp-server $(TARGET_DIR)/usr/lib
	touch $@ $(OPENSSH_SFTP_STAMP)

endif
