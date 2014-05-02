#############################################################
#
# rsnapshot
#
#############################################################

RSNAPSHOT_VERSION = 1.3.1
RSNAPSHOT_SOURCE = rsnapshot-$(RSNAPSHOT_VERSION).tar.gz
RSNAPSHOT_SITE = http://www.rsnapshot.org/downloads
RSNAPSHOT_AUTORECONF = NO
RSNAPSHOT_INSTALL_STAGING = NO
RSNAPSHOT_INSTALL_TARGET = YES
RSNAPSHOT_LIBTOOL_PATCH = NO

RSNAPSHOT_DEPENDENCIES = uclibc rsync perl

$(eval $(call AUTOTARGETS,package,rsnapshot))

$(RSNAPSHOT_HOOK_POST_INSTALL):
	mv $(TARGET_DIR)/etc/rsnapshot.conf.default $(TARGET_DIR)/etc/rsnapshot.conf
	touch $@

# don't generate docs
$(RSNAPSHOT_HOOK_POST_CONFIGURE):
	sed -i 's/^man_MANS =.*/#&/' $(RSNAPSHOT_DIR)/Makefile
