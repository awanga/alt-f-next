#############################################################
#
# rsync
#
############################################################

RSYNC_VERSION:=3.1.3
RSYNC_SOURCE:=rsync-$(RSYNC_VERSION).tar.gz
RSYNC_SITE:=https://rsync.samba.org/ftp/rsync/src
RSYNC_AUTORECONF:=no
RSYNC_USE_CONFIG_CACHE:=no
RSYNC_INSTALL_STAGING:=NO
RSYNC_INSTALL_TARGET:=YES

ifeq ($(BR2_ENABLE_DEBUG),y)
RSYNC_INSTALL_TARGET_OPT:=DESTDIR=$(TARGET_DIR) INSTALLCMD='./install-sh -c' \
	install
else
RSYNC_INSTALL_TARGET_OPT:=DESTDIR=$(TARGET_DIR) INSTALLCMD='./install-sh -c' \
	STRIPPROG="$(TARGET_STRIP)" install-strip
endif

RSYNC_DEPENDENCIES:=uclibc popt
RSYNC_CONF_OPT:=$(DISABLE_IPV6)
RSYNC_CONF_ENV:= CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_RSYNC_OPTIM)" \
	rsync_cv_HAVE_SOCKETPAIR=yes

ifeq ($(BR2_PACKAGE_RSYNC_ACL),y)
RSYNC_DEPENDENCIES += acl
RSYNC_CONF_OPT += --enable-acl-support --enable-xattr-support
else
RSYNC_CONF_OPT += --disable-acl-support --disable-xattr-support
endif

$(eval $(call AUTOTARGETS,package,rsync))
