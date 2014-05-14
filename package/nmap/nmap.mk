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

$(NMAP_TARGET_INSTALL_TARGET):
	$(call MESSAGE,"Installing to target")
	$(MAKE1) DESTDIR=$(TARGET_DIR) -C $(NMAP_DIR) install
	touch $@