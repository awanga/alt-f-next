#############################################################
#
# hddtemp
# 
#############################################################
HDDTEMP_VERSION:=0.3-beta15
HDDTEMP_SOURCE:=hddtemp-$(HDDTEMP_VERSION).tar.bz2
HDDTEMP_SITE:=http://mirrors.aixtools.net/sv/hddtemp
HDDTEMP_DIR:=$(BUILD_DIR)/hddtemp-$(HDDTEMP_VERSION)
HDDTEMP_BINARY:=hddtemp
HDDTEMP_TARGET_BINARY:=sbin/hddtemp
HDDTEMP_CONF_OPT = --disable-nls

$(eval $(call AUTOTARGETS,package,hddtemp))

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_HDDTEMP),y)
TARGETS+=hddtemp
endif
