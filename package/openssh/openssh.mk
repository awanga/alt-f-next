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

#$(OPENSSH_HOOK_POST_INSTALL):
#	$(INSTALL) -D -m 755 package/openssh/S50sshd $(TARGET_DIR)/etc/init.d/S50sshd
#	touch $@

# ugly and quick hack, FIXME!
# I only want sftp-server for use with dropbear, so remove eveything else
$(OPENSSH_HOOK_POST_INSTALL):
	mkdir -p $(TARGET_DIR)/usr/libexec 
	cp $(TARGET_DIR)/usr/lib/sftp-server $(TARGET_DIR)/usr/libexec
	rmdir $(TARGET_DIR)/var/empty
	for i in etc/moduli etc/ssh_config etc/sshd_config usr/bin/sftp \
usr/bin/slogin usr/bin/ssh-add usr/bin/ssh-agent usr/bin/ssh-keygen \
usr/bin/ssh-keyscan usr/lib/sftp-server usr/lib/ssh-keysign \
usr/sbin/sshd usr/share/Ssh.bin var/empty; do rm -f $(TARGET_DIR)/$$i; done
	touch $@