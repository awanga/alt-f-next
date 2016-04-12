#############################################################
#
# socat
#
#############################################################

SOCAT_VERSION=2.0.0-b9
SOCAT_SOURCE=socat-$(SOCAT_VERSION).tar.bz2
SOCAT_SITE=http://www.dest-unreach.org/socat/download/Archive

SOCAT_DEPENDENCIES = host-autoconf

SOCAT_CONF_ENV = sc_cv_termios_ispeed=no \
		 sc_cv_sys_crdly_shift=9 \
		 sc_cv_sys_tabdly_shift=11 \
		 sc_cv_sys_csize_shift=4

SOCAT_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

ifeq ($(BR2_PACKAGE_OPENSSL),y)
	SOCAT_DEPENDENCIES += openssl
else
	SOCAT_CONF_OPT += --disable-openssl
endif

ifeq ($(BR2_PACKAGE_READLINE),y)
	SOCAT_DEPENDENCIES += readline
else
	SOCAT_CONF_OPT += --disable-readline
endif

$(eval $(call AUTOTARGETS,package,socat))

# We need to run autoconf to regenerate the configure script, in order
# to ensure that the test checking linux/ext2_fs.h works
# properly. However, the package only uses autoconf and not automake,
# so we can't use the normal autoreconf logic.

$(SOCAT_HOOK_POST_EXTRACT):
	(cd $(SOCAT_DIR); \
	$(HOST_DIR)/usr/bin/autoconf; \
	sed -i  's/#if OPENSSL_VERSION_NUMBER >= 0x00908000L/#if OPENSSL_VERSION_NUMBER >= 0x00908000L \&\& !defined OPENSSL_NO_COMP/' sslcls.h xio-openssl.c xioopts.c sslcls.c xio-openssl.h; \
	)
	touch $@
