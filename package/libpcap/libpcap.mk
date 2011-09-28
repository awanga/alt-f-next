#############################################################
#
# libpcap
#
#############################################################
LIBPCAP_VERSION:=1.1.1
LIBPCAP_SOURCE:=libpcap-$(LIBPCAP_VERSION).tar.gz
LIBPCAP_SITE:=http://www.tcpdump.org/release
LIBPCAP_DIR:=$(BUILD_DIR)/libpcap-$(LIBPCAP_VERSION)
LIBPCAP_INSTALL_STAGING = NO

LIBPCAP_CONF_OPT = --disable-yydebug --with-pcap=linux
LIBPCAP_CONF_ENV = ac_cv_linux_vers=$(BR2_DEFAULT_KERNEL_HEADERS)

$(eval $(call AUTOTARGETS,package,libpcap))

#$(LIBPCAP_HOOK_POST_CONFIGURE):
#	sed -i 's/^install:/install-strip:/p' $(LIBPCAP_DIR)/Makefile
#	touch $@