#############################################################
#
# iptables
#
#############################################################

#http://www.netfilter.org/projects/iptables/files/iptables-1.4.19.1.tar.bz2
#ftp://ftp.netfilter.org/pub/iptables/iptables-1.4.2.tar.bz2

IPTABLES_VERSION = 1.4.19.1
IPTABLES_SOURCE = iptables-$(IPTABLES_VERSION).tar.bz2
IPTABLES_SITE = http://ftp.netfilter.org/pub/iptables

IPTABLES_LIBTOOL_PATCH = NO

IPTABLES_CONF_OPT = --libexecdir=/usr/lib --with-kernel=$(LINUX_HEADERS_DIR)

$(eval $(call AUTOTARGETS,package,iptables))

$(IPTABLES_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	rm -f $(TARGET_DIR)/usr/bin/iptables-xml
	rm -f $(TARGET_DIR)/usr/sbin/iptables* $(TARGET_DIR)/usr/sbin/ip6tables*
	rm -rf $(TARGET_DIR)/usr/lib/xtables
	rm -f $(IPTABLES_TARGET_INSTALL_TARGET)
