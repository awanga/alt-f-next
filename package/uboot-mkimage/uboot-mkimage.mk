#############################################################
#
# uboot-mkimage for the host
#
#############################################################

UBOOT_MKIMAGE_VERSION = 0.4
UBOOT_MKIMAGE_SOURCE = uboot-mkimage_$(UBOOT_MKIMAGE_VERSION).tar.gz
#UBOOT_MKIMAGE_SITE = $(BR2_DEBIAN_MIRROR)/debian/pool/main/u/uboot-mkimage
UBOOT_MKIMAGE_SITE = http://archive.debian.org/debian/pool/main/u/uboot-mkimage

UBOOT_MKIMAGE_HOST_DEPENDENCIES = uclibc zlib-host
UBOOT_MKIMAGE_HOST_MAKE_ENV = CC="$(HOSTCC) $(HOST_CFLAGS)"

$(eval $(call AUTOTARGETS_HOST,package,uboot-mkimage))

$(UBOOT_MKIMAGE_HOST_CONFIGURE):
	touch $@
