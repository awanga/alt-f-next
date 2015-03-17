#############################################################
#
# sqlite
#
#############################################################

SQLITE_VERSION = 3080700
SQLITE_SITE = http://www.sqlite.org/2014

#SQLITE_VERSION = 3080803
#SQLITE_SITE = http://www.sqlite.org/2015

SQLITE_SOURCE = sqlite-autoconf-$(SQLITE_VERSION).tar.gz

SQLITE_LIBTOOL_PATCH = NO
SQLITE_INSTALL_STAGING = YES
SQLITE_INSTALL_TARGET = YES

SQLITE_DEPENDENCIES = uclibc

SQLITE_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
SQLITE_PROGS = sqlite3

# to use the default safer serialized mode (https://www.sqlite.org/threadsafe.html)
# don't specify any of --enable-threadsafe or --disable-threadsafe

SQLITE_CONF_OPT = --enable-shared \
		--disable-static \
		--enable-dynamic-extensions \
		--localstatedir=/var

SQLITE_CONF_ENV += CFLAGS+=" -DSQLITE_ENABLE_UNLOCK_NOTIFY"

ifeq ($(BR2_PACKAGE_SQLITE_READLINE),y)
SQLITE_DEPENDENCIES += readline
SQLITE_CONF_OPT += --enable-readline
else
SQLITE_CONF_OPT += --disable-readline
endif

$(eval $(call AUTOTARGETS,package/database,sqlite))

$(SQLITE_HOOK_POST_INSTALL):
ifneq ($(BR2_PACKAGE_SQLITE_PROGS),y)
	(cd $(TARGET_DIR)/usr/bin; rm -f $(SQLITE_PROGS))
endif
	touch $@

$(SQLITE_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	rm -f $(TARGET_DIR)/usr/bin/sqlite3
	rm -f $(TARGET_DIR)/usr/lib/libsqlite3*
	rm -f $(STAGING_DIR)/usr/bin/sqlite3
	rm -f $(STAGING_DIR)/usr/lib/libsqlite3*
	rm -f $(STAGING_DIR)/usr/lib/pkgconfig/sqlite3.pc
	rm -f $(STAGING_DIR)/usr/include/sqlite3*.h
	rm -f $(SQLITE_TARGET_INSTALL_TARGET) $(SQLITE_HOOK_POST_INSTALL)

