#############################################################
#
# netatalk
#
############################################################

NETATALK_VERSION = 3.1.12
NETATALK_SOURCE = netatalk-$(NETATALK_VERSION).tar.bz2
NETATALK_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/netatalk/netatalk/$(NETATALK_VERSION)

NETATALK_LIBTOOL_PATCH = NO
NETATALK_AUTORECONF = NO

NETATALK_CONF_OPT = \
	--with-bdb=$(STAGING_DIR)/usr \
	--with-ssl-dir=$(STAGING_DIR)/usr \
	--localstatedir=/var/lib \
	--enable-zeroconf \
	--disable-cups \
	--without-pam \
	--without-kerberos \
	--without-gssapi \
	--without-ldap \
	--disable-tcp-wrappers \
	--without-libevent \
	--with-libevent-header=$(STAGING_DIR)/usr/include/event2  \
	--with-libevent-lib=$(STAGING_DIR)/usr/lib/  \
	--disable-static \
	--program-prefix="" \
	--with-lockfile=/var/run/netatalk.pid \
	--with-mysql-config=no

NETATALK_DEPENDENCIES = uclibc libgcrypt db avahi libevent2 acl openssl libiconv

$(eval $(call AUTOTARGETS,package,netatalk))

$(NETATALK_HOOK_POST_CONFIGURE):
	# setting --enable-fhs on configure changes install folders to /bin/, /lib, etc
	# as only /var/run/netatalk.pid is desired (include/atalk/paths.h), hack:
	sed -i 's/.*FHS_COMPATIBILITY.*/#define FHS_COMPATIBILITY 1/' $(NETATALK_DIR)/config.h
	touch $@

$(NETATALK_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/aclocal $(TARGET_DIR)/usr/bin/asip-status.pl $(TARGET_DIR)/usr/bin/netatalk-config
	touch $@
