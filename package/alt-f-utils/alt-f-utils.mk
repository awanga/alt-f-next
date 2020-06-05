#############################################################
#
# Alt-F-utils
#
#############################################################

ALT_F_UTILS_VERSION = 0.1.10
ALT_F_UTILS_SOURCE = alt-f-utils-$(ALT_F_UTILS_VERSION).tar.gz
ALT_F_UTILS_SITE = file://$(DL_DIR)

ALT_F_UTILS_AUTORECONF := NO
ALT_F_UTILS_LIBTOOL_PATCH = NO

ALT_F_UTILS_INSTALL_STAGING := NO
ALT_F_UTILS_INSTALL_TARGET := YES

ALT_F_UTILS_MAKE_ENV := CC="$(TARGET_CC) $(TARGET_CFLAGS) -D_GNU_SOURCE" STRIP="$(TARGET_STRIP)"
HOST_ALT_F_UTILS_MAKE_ENV := STRIP=true DESTDIR="$(HOST_DIR)"

$(DL_DIR)/$(ALT_F_UTILS_SOURCE): package/alt-f-utils/alt-f-utils-$(ALT_F_UTILS_VERSION)/sysctrl.c \
		package/alt-f-utils/alt-f-utils-$(ALT_F_UTILS_VERSION)/dns323-fw.c \
		package/alt-f-utils/alt-f-utils-$(ALT_F_UTILS_VERSION)/dns320l-daemon.c
	(cd package/alt-f-utils/; \
		rm alt-f-utils-$(ALT_F_UTILS_VERSION)/*~; \
		$(TAR) --exclude-vcs -cvzf $(ALT_F_UTILS_SOURCE) alt-f-utils-$(ALT_F_UTILS_VERSION); \
		cp  $(ALT_F_UTILS_SOURCE) $(DL_DIR) \
	)
	-make alt-f-utils-dirclean alt-f-utils-host-dirclean
	touch $@

$(eval $(autotools-package))
$(eval $(host-autotools-package))

$(HOST_ALT_F_UTILS_POST_INSTALL_HOOKS):
	mkdir -p $(HOST_DIR)/usr/bin
	( cd $(HOST_DIR)/usr/sbin/; \
		rm rpcinfo sysctrl dns320l-daemon; \
		mv dns323-fw ../bin \
	)
	touch $@

$(ALT_F_UTILS_TARGET_CONFIGURE) $(HOST_ALT_F_UTILS_TARGET_CONFIGURE):
	touch $@

$(ALT_F_UTILS_TARGET_SOURCE) $(HOST_ALT_F_UTILS_TARGET_SOURCE): $(DL_DIR)/$(ALT_F_UTILS_SOURCE)
