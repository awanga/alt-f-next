#############################################################
#
# cifs-utils
# 
############################################################

CIFS_UTILS_VERSION:=6.6
CIFS_UTILS_SOURCE:=cifs-utils-$(CIFS_UTILS_VERSION).tar.bz2
CIFS_UTILS_SITE:=https://download.samba.org/pub/linux-cifs/cifs-utils

#CIFS_UTILS_DEPENDENCIES = gettext 
#CIFS_UTILS_CONF_OPT = --disable-nls
#CIFS_UTILS_CONF_ENV = LIBS="-liconv -lintl"

$(eval $(call AUTOTARGETS,package,cifs-utils))

$(CIFS_UTILS_HOOK_POST_INSTALL):
	mv $(TARGET_DIR)/sbin/mount.cifs $(TARGET_DIR)/usr/sbin/mount.cifs
	touch $@