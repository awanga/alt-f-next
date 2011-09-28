#############################################################
#
# sysstat
#
#############################################################
SYSSTAT_VERSION:=10.0.0
SYSSTAT_SOURCE:=sysstat-$(SYSSTAT_VERSION).tar.gz
SYSSTAT_SITE:=http://pagesperso-orange.fr/sebastien.godard/
SYSSTAT_DIR:=$(BUILD_DIR)/sysstat-$(SYSSTAT_VERSION)
SYSSTAT_INSTALL_STAGING = NO

SYSSTAT_CONF_OPT = --disable-documentation
SYSSTAT_CONF_ENV = conf_dir=/etc/sysstat

$(eval $(call AUTOTARGETS,package,sysstat))

$(SYSSTAT_HOOK_POST_CONFIGURE):
	sed -i 's/^install:/install-strip:/p' $(SYSSTAT_DIR)/Makefile
	touch $@