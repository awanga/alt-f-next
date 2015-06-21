#############################################################
#
# sysstat
#
#############################################################
SYSSTAT_VERSION:=10.0.0
SYSSTAT_SOURCE:=sysstat-$(SYSSTAT_VERSION).tar.gz
SYSSTAT_SITE:=https://github.com/sysstat/sysstat/archive
SYSSTAT_DIR:=$(BUILD_DIR)/sysstat-$(SYSSTAT_VERSION)
SYSSTAT_INSTALL_STAGING = NO

SYSSTAT_CONF_OPT = --disable-documentation
SYSSTAT_CONF_ENV = conf_dir=/etc/sysstat

$(eval $(call AUTOTARGETS,package,sysstat))

$(SYSSTAT_TARGET_SOURCE):
	$(call DOWNLOAD,$(SYSSTAT_SITE),v$(SYSSTAT_VERSION).tar.gz)
	(cd $(DL_DIR); ln -sf v$(SYSSTAT_VERSION).tar.gz sysstat-$(SYSSTAT_VERSION).tar.gz )
	mkdir -p $(BUILD_DIR)/sysstat-$(SYSSTAT_VERSION)
	touch $@

$(SYSSTAT_HOOK_POST_CONFIGURE):
	sed -i 's/^install:/install-strip:/p' $(SYSSTAT_DIR)/Makefile
	touch $@
