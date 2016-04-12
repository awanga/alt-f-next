#############################################################
#
# uboot-envtools for the target
#
#############################################################

UBOOT_ENVTOOLS_VERSION = 20081215
UBOOT_ENVTOOLS_SOURCE = uboot-envtools_$(UBOOT_ENVTOOLS_VERSION).orig.tar.gz
UBOOT_ENVTOOLS_SITE = $(BR2_DEBIAN_MIRROR)/debian/pool/main/u/uboot-envtools

UBOOT_ENVTOOLS_DEPENDENCIES = uclibc

UBOOT_ENVTOOLS_MAKE_OPT = CROSS_COMPILE=$(TARGET_CROSS) CPPFLAGS="$(TARGET_CFLAGS) -I$(LINUX_HEADERS_DIR)/include -DUSE_HOSTCC"

$(eval $(call AUTOTARGETS,package,uboot-envtools))

$(UBOOT_ENVTOOLS_TARGET_CONFIGURE):
	touch $@

$(UBOOT_ENVTOOLS_TARGET_INSTALL_TARGET):
	cp $(UBOOT_ENVTOOLS_DIR)/fw_printenv $(TARGET_DIR)/usr/bin
	cp $(UBOOT_ENVTOOLS_DIR)/fw_env.config $(TARGET_DIR)/etc/fw_env.config-sample
	(cd $(TARGET_DIR)/usr/bin; ln -sf fw_printenv fw_setenv)
	touch $@
