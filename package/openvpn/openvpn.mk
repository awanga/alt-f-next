#############################################################
#
# openvpn
#
#############################################################

OPENVPN_VERSION = 2.2.1
OPENVPN_SOURCE = openvpn-$(OPENVPN_VERSION).tar.gz
OPENVPN_SITE = http://swupdate.openvpn.org/community/releases
OPENVPN_DEPENDENCIES = lzo openssl uclibc
#OPENVPN_CONF_OPT = --enable-small

ifeq ($(BR2_PTHREADS_NATIVE),y)
	OPENVPN_CONF_OPT += --enable-threads=posix
else
	OPENVPN_CONF_OPT += --enable-pthread
endif

$(eval $(call AUTOTARGETS,package,openvpn))

$(OPENVPN_TARGET_INSTALL_TARGET):
	$(call MESSAGE,"Installing")
	$(INSTALL) -m 755 $(OPENVPN_DIR)/openvpn \
		$(TARGET_DIR)/usr/sbin/openvpn
	#if [ ! -f $(TARGET_DIR)/etc/init.d/openvpn ]; then \
	#	$(INSTALL) -m 755 -D package/openvpn/openvpn.init \
	#		$(TARGET_DIR)/etc/init.d/openvpn; \
	#fi
	$(INSTALL) -m 755 -D package/openvpn/openvpn.init \
		$(TARGET_DIR)/usr/share/openvpn/openvpn.init
	mkdir -p $(TARGET_DIR)/etc/openvpn
	mkdir -p $(TARGET_DIR)/usr/share/openvpn
	(cd $(OPENVPN_DIR); cp -a easy-rsa sample-scripts sample-config-files $(TARGET_DIR)/usr/share/openvpn)
	touch $@
