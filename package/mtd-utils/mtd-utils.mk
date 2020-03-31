#############################################################
#
# mtd-utils provides mtd, jffs2, ubi and ubifs utilities
#
############################################################

MTD_UTILS_VERSION:=2.0.2
MTD_UTILS_SOURCE:=mtd-utils-$(MTD_UTILS_VERSION).tar.bz2
MTD_UTILS_SITE:=ftp://ftp.infradead.org/pub/mtd-utils

MTD_UTILS_AUTORECONF = NO
MTD_UTILS_LIBTOOL_PATCH = NO

MTD_UTILS_DEPENDENCIES = zlib lzo acl libuuid pkg-config mtd-utils-host
MTD_UTILS_HOST_DEPENDENCIES = lzo-host acl-host

#MTD_UTILS_CONF_OPT = --disable-nls --disable-gtk --disable-gconf2 \
--enable-utp --enable-cli --enable-lightweight
#MTD_UTILS_CONF_ENV = ZLIB_LIBS="-L$(STAGING_DIR)/usr/lib -lz" ZLIB_CFLAGS="-I$(STAGING_DIR)/usr/include"
# FIXME: zlib: install zlib.pc

$(eval $(call AUTOTARGETS,package,mtd-utils))
$(eval $(call AUTOTARGETS_HOST,package,mtd-utils))

$(MTD_UTILS_HOST_HOOK_POST_INSTALL):
	mv $(HOST_DIR)/usr/sbin/* $(HOST_DIR)/usr/bin
	touch $@
