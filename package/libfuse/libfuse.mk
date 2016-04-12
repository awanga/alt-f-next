#############################################################
#
# libfuse
#
#############################################################

LIBFUSE_VERSION:=2.8.5
LIBFUSE_SOURCE:=fuse-$(LIBFUSE_VERSION).tar.gz
#LIBFUSE_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/fuse/fuse-2.X/$(LIBFUSE_VERSION)
LIBFUSE_SITE:=https://github.com/libfuse/libfuse/releases/download/fuse_2_9_4

LIBFUSE_DIR:=$(BUILD_DIR)/fuse-$(LIBFUSE_VERSION)
LIBFUSE_BINARY:=libfuse
LIBFUSE_LIBTOOL_PATCH = NO
LIBFUSE_INSTALL_STAGING = YES
LIBFUSE_INSTALL_TARGET = YES
LIBFUSE_CONF_OPT:= --enable-util --enable-lib --disable-mtab --disable-example

$(eval $(call AUTOTARGETS,package,libfuse))

$(LIBFUSE_TARGET_INSTALL_TARGET):
	mkdir -p $(TARGET_DIR)/usr/lib
	mkdir -p $(TARGET_DIR)/usr/bin
	cp -dpf $(STAGING_DIR)/usr/bin/arm-linux-fusermount $(TARGET_DIR)/usr/bin/fusermount
	$(STRIPCMD) $(STRIP_STRIP_ALL) $(TARGET_DIR)/usr/bin/fusermount
	cp -dpf $(STAGING_DIR)/usr/lib/libfuse.so* $(TARGET_DIR)/usr/lib/
	$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/libfuse.so
	touch $@
