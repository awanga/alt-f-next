#############################################################
#
# Alt-F-utils
#
#############################################################
ALT_F_UTILS_VERSION = 0.1.7
ALT_F_UTILS_SOURCE = alt-f-utils-$(ALT_F_UTILS_VERSION).tar.gz
ALT_F_UTILS_SITE = file://$(DL_DIR)

ALT_F_UTILS_AUTORECONF := NO
ALT_F_UTILS_INSTALL_STAGING := NO
ALT_F_UTILS_INSTALL_TARGET := YES
ALT_F_UTILS_DEPENDENCIES := uclibc

$(DL_DIR)/$(ALT_F_UTILS_SOURCE): package/alt-f-utils/alt-f-utils-$(ALT_F_UTILS_VERSION)/sysctrl.c package/alt-f-utils/alt-f-utils-$(ALT_F_UTILS_VERSION)/dns323-fw.c
	(cd package/alt-f-utils/; \
		rm *~; \
		$(TAR) --exclude-vcs -cvzf $(ALT_F_UTILS_SOURCE) alt-f-utils-$(ALT_F_UTILS_VERSION); \
		cp  $(ALT_F_UTILS_SOURCE) $(DL_DIR) \
	)

ifeq ($(BR2_PACKAGE_ALT_F_UTILS_TARGET),y)
ALT_F_UTILS_MAKE_ENV := CC="$(TARGET_CC) $(TARGET_CFLAGS)" STRIP="$(TARGET_STRIP)"
$(eval $(call AUTOTARGETS,package,alt-f-utils))
endif

ifeq ($(BR2_PACKAGE_ALT_F_UTILS_HOST),y)
ALT_F_UTILS_HOST_MAKE_ENV := STRIP=true
$(eval $(call AUTOTARGETS_HOST,package,alt-f-utils))

$(ALT_F_UTILS_HOST_HOOK_POST_INSTALL):
	mkdir -p $(HOST_DIR)/usr/bin
	( cd $(HOST_DIR)/usr/sbin/; \
		rm rpcinfo sysctrl; \
		mv dns323-fw ../bin \
	)
	touch $@

endif

$(ALT_F_UTILS_TARGET_SOURCE): $(DL_DIR)/$(ALT_F_UTILS_SOURCE)