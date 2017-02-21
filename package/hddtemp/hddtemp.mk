#############################################################
#
# hddtemp
# 
############################################################

HDDTEMP_VERSION:=0.3-beta15
HDDTEMP_SOURCE:=hddtemp-$(HDDTEMP_VERSION).tar.bz2
HDDTEMP_SITE:=http://download.savannah.gnu.org/releases/hddtemp

HDDTEMP_DEPENDENCIES = gettext 
HDDTEMP_CONF_OPT = --disable-nls
HDDTEMP_CONF_ENV = LIBS="-liconv -lintl"

$(eval $(call AUTOTARGETS,package,hddtemp))

$(HDDTEMP_HOOK_POST_INSTALL):
	mkdir -p $(TARGET_DIR)/usr/share/misc
	cp $(HDDTEMP_DIR_PREFIX)/$(HDDTEMP_NAME)/hddtemp.db $(TARGET_DIR)/usr/share/misc/hddtemp.db
	touch $@