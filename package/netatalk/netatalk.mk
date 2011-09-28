#############################################################
#
# netatalk
#
#############################################################
NETATALK_VERSION = 2.1.5
NETATALK_SOURCE = netatalk-$(NETATALK_VERSION).tar.gz
NETATALK_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/netatalk
NETATALK_AUTORECONF = NO
NETATALK_INSTALL_STAGING = NO
NETATALK_INSTALL_TARGET = YES
NETATALK_LIBTOOL_PATCH = YES

NETATALK_CONF_OPT = --with-bdb=$(STAGING_DIR)/usr \
		--with-ssl-dir=$(STAGING_DIR)/usr \
		--with-libiconv=$(STAGING_DIR)/usr \
		--with-libgcrypt-dir=$(STAGING_DIR)/usr \
		--disable-cups \
		--without-pam \
		--without-gssapi \
		--disable-tcp-wrappers \
		--disable-static \
		--program-prefix=""

NETATALK_DEPENDENCIES = uclibc libgcrypt db avahi

$(eval $(call AUTOTARGETS,package,netatalk))

$(NETATALK_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/aclocal
	touch $@