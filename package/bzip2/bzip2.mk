################################################################################
#
# bzip2
#
################################################################################

BZIP2_VERSION = 1.0.8
BZIP2_SITE = https://sourceware.org/pub/bzip2
BZIP2_INSTALL_STAGING = YES
BZIP2_LICENSE = bzip2 license
BZIP2_LICENSE_FILES = LICENSE

ifeq ($(BR2_STATIC_LIBS),)
define BZIP2_BUILD_SHARED_CMDS
	$(TARGET_MAKE_ENV) \
		$(MAKE) -C $(@D) -f Makefile-libbz2_so $(TARGET_CONFIGURE_OPTS)
endef
endif

define BZIP2_BUILD_CMDS
	$(TARGET_MAKE_ENV) \
		$(MAKE) -C $(@D) libbz2.a bzip2 bzip2recover $(TARGET_CONFIGURE_OPTS)
	$(BZIP2_BUILD_SHARED_CMDS)
endef

ifeq ($(BR2_STATIC_LIBS),)
define BZIP2_INSTALL_STAGING_SHARED_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) \
		-f Makefile-libbz2_so PREFIX=$(STAGING_DIR)/usr -C $(@D) install
endef
endif

define BZIP2_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) \
		PREFIX=$(STAGING_DIR)/usr -C $(@D) install
	$(BZIP2_INSTALL_STAGING_SHARED_CMDS)
endef

ifeq ($(BR2_STATIC_LIBS),)
define BZIP2_INSTALL_TARGET_SHARED_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) \
		-f Makefile-libbz2_so PREFIX=$(TARGET_DIR)/usr -C $(@D) install
endef
endif

# make sure busybox doesn't get overwritten by make install
ifeq ($(BR2_PACKAGE_ALT_F_UTILS_TARGET),y)
define BZIP2_INSTALL_TARGET_CMDS
	mv $(TARGET_DIR)/usr/bin/bunzip2 $(TARGET_DIR)/usr/bin/bunzip2.bkp
	mv $(TARGET_DIR)/usr/bin/bzcat $(TARGET_DIR)/usr/bin/bzcat.bkp
	$(TARGET_MAKE_ENV) $(MAKE) \
		PREFIX=$(TARGET_DIR)/usr -C $(@D) install
	mv $(TARGET_DIR)/usr/bin/bunzip2 $(TARGET_DIR)/usr/bin/bunzip2-bzip2
	mv $(TARGET_DIR)/usr/bin/bzcat $(TARGET_DIR)/usr/bin/bzcat-bzip2
	mv $(TARGET_DIR)/usr/bin/bunzip2.bkp $(TARGET_DIR)/usr/bin/bunzip2
	mv $(TARGET_DIR)/usr/bin/bzcat.bkp $(TARGET_DIR)/usr/bin/bzcat
endef
else
define BZIP2_INSTALL_TARGET_CMDS
	rm -f $(addprefix $(TARGET_DIR)/usr/bin/,bzip2 bunzip2 bzcat)
	$(TARGET_MAKE_ENV) $(MAKE) \
		PREFIX=$(TARGET_DIR)/usr -C $(@D) install
	$(BZIP2_INSTALL_TARGET_SHARED_CMDS)
endef
endif

define HOST_BZIP2_BUILD_CMDS
	$(HOST_MAKE_ENV) $(HOST_CONFIGURE_OPTS) \
		$(MAKE) -C $(@D) -f Makefile-libbz2_so
	$(HOST_MAKE_ENV) $(HOST_CONFIGURE_OPTS) \
		$(MAKE) -C $(@D) libbz2.a bzip2 bzip2recover
endef

define HOST_BZIP2_INSTALL_CMDS
	$(HOST_MAKE_ENV) \
		$(MAKE) PREFIX=$(HOST_DIR) -C $(@D) install
	$(HOST_MAKE_ENV) \
		$(MAKE) -f Makefile-libbz2_so PREFIX=$(HOST_DIR) -C $(@D) install
endef

$(eval $(generic-package))
$(eval $(host-generic-package))
