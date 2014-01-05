#############################################################
#
# openssh
#
#############################################################

OPENSSH_VERSION=6.1p1
OPENSSH_SITE=ftp://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable

OPENSSH_CONF_ENV = LD=$(TARGET_CC)
OPENSSH_CONF_OPT = --sysconfdir=/etc/ssh --with-privsep-path=/var/run/vsftpd \
	-disable-lastlog --disable-utmp --disable-utmpx --disable-wtmp --disable-wtmpx

OPENSSH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

# The bellow dependency on dropbear is a fake. Dropbear installs ssh, scp, etc as a link
# to dropbear, so if it is installed after openssh it will override those binaries

OPENSSH_DEPENDENCIES = zlib openssl dropbear

$(eval $(call AUTOTARGETS,package,openssh))

# this is a hack. Use AUTOTARGETS to do everything but install.
# At the build end, the post build hook runs, which installs just sftp-server

ifneq ($(BR2_PACKAGE_OPENSSH_SFTP),y)

$(OPENSSH_HOOK_POST_INSTALL):
	sed -i 's/#.*Ciphers /Ciphers aes128-cbc,/' $(TARGET_DIR)/etc/ssh/ssh_config
	touch $@

else

$(OPENSSH_TARGET_INSTALL_TARGET):
	$(INSTALL) -m 0755 $(OPENSSH_DIR)/sftp-server $(TARGET_DIR)/usr/lib
	touch $@

endif
