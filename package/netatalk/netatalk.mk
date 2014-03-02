#############################################################
#
# netatalk
#
#############################################################

NETATALK_VERSION = 3.0.8
NETATALK_SOURCE = netatalk-$(NETATALK_VERSION).tar.bz2
NETATALK_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/project/netatalk/netatalk/$(NETATALK_VERSION)

NETATALK_LIBTOOL_PATCH = NO
NETATALK_AUTORECONF = NO

NETATALK_INSTALL_STAGING = NO
NETATALK_INSTALL_TARGET = YES
        
NETATALK_CONF_OPT = \
		--localstatedir=/var/lib \
		--with-sysroot=$(STAGING_DIR)/usr \
		--with-ssl-dir=$(STAGING_DIR)/usr \
		--with-libiconv=$(STAGING_DIR)/usr \
		--with-libgcrypt-dir=$(STAGING_DIR)/usr \
		--with-bdb=$(STAGING_DIR)/usr \
		--with-libevent-header=$(STAGING_DIR)/libevent2/include \
		--with-libevent-lib=$(STAGING_DIR)/libevent2/lib \
		--enable-zeroconf \
		--disable-cups \
		--without-acls \
		--without-pam \
		--without-kerberos \
		--without-gssapi \
		--without-ldap \
		--disable-tcp-wrappers \
		--disable-static \
		--program-prefix=""

NETATALK_DEPENDENCIES = uclibc libgcrypt db avahi libevent2

$(eval $(call AUTOTARGETS,package,netatalk))

$(NETATALK_HOOK_POST_CONFIGURE):
	sed -i 's/-levent/-levent2/' $(NETATALK_DIR)/etc/netatalk/Makefile
	# setting --enable-fhs on configure changes install folders to /bin/, /lib, etc
	# as only /var/run/netatalk.pid is desired (include/atalk/paths.h), hack:
	sed -i 's/.*FHS_COMPATIBILITY.*/#define FHS_COMPATIBILITY 1/' $(NETATALK_DIR)/config.h
	touch $@

$(NETATALK_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/aclocal $(TARGET_DIR)/usr/bin/asip-status.pl $(TARGET_DIR)/usr/bin/netatalk-config
	touch $@
