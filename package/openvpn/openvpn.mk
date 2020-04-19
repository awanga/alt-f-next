#############################################################
#
# openvpn
#
############################################################

OPENVPN_VERSION = 2.4.8
OPENVPN_SOURCE = openvpn-$(OPENVPN_VERSION).tar.xz
OPENVPN_SITE = https://swupdate.openvpn.org/community/releases

OPENVPN_LIBTOOL_PATCH = NO
OPENVPN_DEPENDENCIES = lzo openssl uclibc
OPENVPN_CONF_OPT = --enable-password-save --disable-plugin-auth-pam --disable-systemd
OPENVPN_CONF_ENV = IFCONFIG=/sbin/ifconfig ROUTE=/sbin/route IPROUTE=/bin/iproute \
	NETSTAT=/bin/netstat SYSTEMD_ASK_PASSWORD=

ifeq ($(BR2_PTHREADS_NATIVE),y)
	OPENVPN_CONF_OPT += --enable-threads=posix
else
	OPENVPN_CONF_OPT += --enable-pthread
endif

$(eval $(call AUTOTARGETS,package,openvpn))

# see https://wiki.debian.org/OpenVPN on how to test

$(OPENVPN_HOOK_POST_CONFIGURE):
	(echo '#include <errno.h>'; \
	echo '#define err(exitcode, format, args...) \
		errx(exitcode, format ": %s", ## args, strerror(errno))'; \
	echo '#define errx(exitcode, format, args...) \
		{ warnx(format, ## args); exit(exitcode); }'; \
	echo '#define warn(format, args...) \
		warnx(format ": %s", ## args, strerror(errno))'; \
	echo '#define warnx(format, args...) \
		fprintf(stderr, format "\n", ## args)'; \
	) > $(OPENVPN_DIR)/err.h
	$(SED) 's/<err.h>/"err.h"/' $(OPENVPN_DIR)/src/plugins/down-root/down-root.c
	touch $@
	
$(OPENVPN_TARGET_INSTALL_TARGET):
	$(call MESSAGE,"Installing")
	$(INSTALL) -m 755 $(OPENVPN_DIR)/src/openvpn/openvpn \
		$(TARGET_DIR)/usr/sbin/openvpn
	#if [ ! -f $(TARGET_DIR)/etc/init.d/openvpn ]; then \
	#	$(INSTALL) -m 755 -D package/openvpn/openvpn.init \
	#		$(TARGET_DIR)/etc/init.d/openvpn; \
	#fi
	#$(INSTALL) -m 755 -D package/openvpn/openvpn.init \
	#	$(TARGET_DIR)/usr/share/openvpn/openvpn.init
	mkdir -p $(TARGET_DIR)/etc/openvpn
	mkdir -p $(TARGET_DIR)/usr/share/openvpn
	(cd $(OPENVPN_DIR); cp -a sample/sample-scripts sample/sample-config-files sample/sample-keys contrib $(TARGET_DIR)/usr/share/openvpn)
	touch $@
