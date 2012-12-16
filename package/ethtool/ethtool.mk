#############################################################
#
# ethtool
#
#############################################################

#ETHTOOL_VERSION:=2.6.36
ETHTOOL_VERSION:=3.7
ETHTOOL_SOURCE:=ethtool-$(ETHTOOL_VERSION).tar.gz
ETHTOOL_SITE:=http://www.kernel.org/pub/software/network/ethtool
ETHTOOL_AUTORECONF:=no
ETHTOOL_INSTALL_STAGING:=NO
ETHTOOL_INSTALL_TARGET:=YES

ETHTOOL_DEPENDENCIES:=uclibc

$(eval $(call AUTOTARGETS,package,ethtool))
