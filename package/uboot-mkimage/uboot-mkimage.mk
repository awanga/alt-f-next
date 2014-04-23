#############################################################
#
# uboot-mkimage for the host
#
#############################################################

UBOOT_MKIMAGE_VERSION = 0.4
UBOOT_MKIMAGE_SOURCE = uboot-mkimage_$(UBOOT_MKIMAGE_VERSION).tar.gz
UBOOT_MKIMAGE_SITE = http://ftp.de.debian.org/debian/pool/main/u/uboot-mkimage

UBOOT_MKIMAGE_HOST_DEPENDENCIES = uclibc zlib-host
UBOOT_MKIMAGE_HOST_MAKE_ENV = CC="$(HOSTCC) $(HOST_CFLAGS)"

$(eval $(call AUTOTARGETS_HOST,package,uboot-mkimage))

$(UBOOT_MKIMAGE_HOST_HOOK_POST_EXTRACT):
	echo -e "#!/bin/sh\ntrue" > $(UBOOT_MKIMAGE_HOST_DIR)/configure
	chmod +x $(UBOOT_MKIMAGE_HOST_DIR)/configure
	touch $@
