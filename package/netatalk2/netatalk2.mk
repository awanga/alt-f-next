#############################################################
#
# netatalk2
#
#############################################################

NETATALK2_VERSION = 2.2.4
NETATALK2_SOURCE = netatalk-$(NETATALK2_VERSION).tar.bz2
NETATALK2_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/netatalk

NETATALK2_AUTORECONF = NO
NETATALK2_INSTALL_STAGING = NO
NETATALK2_INSTALL_TARGET = YES
NETATALK2_LIBTOOL_PATCH = NO

NETATALK2_CONF_OPT = --with-bdb=$(STAGING_DIR)/usr \
		--with-ssl-dir=$(STAGING_DIR)/usr \
		--with-libiconv=$(STAGING_DIR)/usr \
		--with-libgcrypt-dir=$(STAGING_DIR)/usr \
		--enable-ddp \
		--disable-cups \
		--without-pam \
		--without-gssapi \
		--without-ldap \
		--disable-tcp-wrappers \
		--disable-static \
		--program-prefix=""

NETATALK2_DEPENDENCIES = uclibc libgcrypt db avahi

$(eval $(call AUTOTARGETS,package,netatalk2))

$(NETATALK2_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/aclocal
	touch $@