#############################################################
#
# netatalk
#
#############################################################
NETATALK_VERSION = 3.0.1
NETATALK_SOURCE = netatalk-$(NETATALK_VERSION).tar.bz2
NETATALK_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/project/netatalk/netatalk/$(NETATALK_VERSION)
NETATALK_AUTORECONF = NO
NETATALK_INSTALL_STAGING = NO
NETATALK_INSTALL_TARGET = YES
NETATALK_LIBTOOL_PATCH = NO

#NETATALK_CONF_ENV = \
#		LIBEVENT_CFLAGS="-I$(STAGING_DIR)/libevent2/include" \
#		LIBEVENT_LDFLAGS="-L$(STAGING_DIR)/libevent2/lib -levent2"
        
NETATALK_CONF_OPT = --with-bdb=$(STAGING_DIR)/usr \
		--with-ssl-dir=$(STAGING_DIR)/usr \
		--with-libiconv=$(STAGING_DIR)/usr \
		--with-libgcrypt-dir=$(STAGING_DIR)/usr \
		--with-bdb=$(STAGING_DIR)/usr \
		--with-libevent-header=$(STAGING_DIR)/libevent2/include \
		--with-libevent-lib=$(STAGING_DIR)/libevent2/lib \
		--disable-cups \
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
	touch $@

$(NETATALK_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/aclocal
	touch $@