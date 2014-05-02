#############################################################
#
# nmap
#
#############################################################

NMAP_VERSION:=5.51
NMAP_SOURCE:=nmap-$(NMAP_VERSION).tar.bz2
NMAP_SITE:=http://nmap.org/dist

NMAP_DIR:=$(BUILD_DIR)/nmap-$(NMAP_VERSION)
NMAP_INSTALL_STAGING = NO
NMAP_LIBTOOL_PATCH = NO

NMAP_CONF_OPT = --with-libpcap=included --with-pcap=linux --without-liblua --without-zenmap
NMAP_CONF_ENV = ac_cv_linux_vers=$(BR2_DEFAULT_KERNEL_HEADERS)

$(eval $(call AUTOTARGETS,package,nmap))

$(NMAP_HOOK_POST_CONFIGURE):
	sed -i 's/^install:/install-strip:/p' $(NMAP_DIR)/Makefile
	touch $@

$(NMAP_HOOK_POST_INSTALL):
	rm $(TARGET_DIR)/usr/bin/ndiff
	touch $@