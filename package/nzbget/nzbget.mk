#############################################################
#
# nzbget
#
#############################################################

NZBGET_VERSION = 14.2
NZBGET_SOURCE = nzbget-$(NZBGET_VERSION).tar.gz
NZBGET_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/nzbget/nzbget-stable/$(NZBGET_VERSION)

NZBGET_AUTORECONF = NO
NZBGET_INSTALL_STAGING = NO
NZBGET_INSTALL_TARGET = YES
NZBGET_LIBTOOL_PATCH = NO
NZBGET_DEPENDENCIES = uclibc libpar2 libxml2 openssl ncurses p7zip unrar

NZBGET_CONF_OPT = --program-prefix=""
NZBGET_CONF_ENV = LIBPREF=$(STAGING_DIR) libxml2_CFLAGS="-I$(STAGING_DIR)/usr/include/libxml2" \
	libxml2_LIBS="-L$(STAGING_DIR)/usr/lib -lxml2"

$(eval $(call AUTOTARGETS,package,nzbget))

$(NZBGET_HOOK_POST_INSTALL):
	$(RM) $(TARGET_DIR)/usr/sbin/nzbgetd
	touch $@