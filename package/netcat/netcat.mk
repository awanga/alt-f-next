#############################################################
#
# netcat
#
#############################################################

NETCAT_VERSION:=0.7.1
NETCAT_SOURCE:=netcat-$(NETCAT_VERSION).tar.gz
NETCAT_SITE=$(BR2_SOURCEFORGE_MIRROR)/project/netcat/netcat/$(NETCAT_VERSION)

NETCAT_AUTORECONF:=NO
NETCAT_INSTALL_STAGING:=NO
NETCAT_INSTALL_TARGET:=YES

NETCAT_DEPENDENCIES = uclibc
NETCAT_CONF_OPT = --program-prefix=""

$(eval $(call AUTOTARGETS,package,netcat))
