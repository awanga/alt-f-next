#############################################################
#
# libpcap
#
############################################################

LIBPCAP_VERSION:=1.4.0
LIBPCAP_SOURCE:=libpcap-$(LIBPCAP_VERSION).tar.gz
LIBPCAP_SITE:=http://www.tcpdump.org/release
LIBPCAP_DIR:=$(BUILD_DIR)/libpcap-$(LIBPCAP_VERSION)
LIBPCAP_INSTALL_STAGING = YES

LIBPCAP_CONF_OPT = --disable-yydebug --with-pcap=linux --without-libnl
LIBPCAP_CONF_ENV = ac_cv_linux_vers=$(BR2_DEFAULT_KERNEL_HEADERS)
LIBPCAP_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,libpcap))

$(LIBPCAP_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/pcap-config
	touch $@
