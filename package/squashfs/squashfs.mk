#############################################################
#
# squashfs
#
#############################################################

SQUASHFS_VERSION = 4.2
SQUASHFS_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/squashfs/squashfs/squashfs$(SQUASHFS_VERSION)
SQUASHFS_SOURCE = squashfs$(SQUASHFS_VERSION).tar.gz

SQUASHFS_AUTORECONF = NO
SQUASHFS_INSTALL_STAGING = NO
SQUASHFS_INSTALL_TARGET = YES
SQUASHFS_LIBTOOL_PATCH = NO
SQUASHFS_SUBDIR = squashfs-tools

ifeq ($(BR2_PACKAGE_SQUASHFS_TARGET),y)
SQUASHFS_DEPENDENCIES = uclibc xz
SQUASHFS_MAKE_OPT = CC="$(TARGET_CC) $(TARGET_CFLAGS)"
SQUASHFS_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR)/usr/bin install

$(eval $(call AUTOTARGETS,package,squashfs))

$(SQUASHFS_HOOK_POST_EXTRACT):
	echo -e "#!/bin/sh\ntrue" > $(SQUASHFS_DIR)/$(SQUASHFS_SUBDIR)/configure
	chmod +x $(SQUASHFS_DIR)/$(SQUASHFS_SUBDIR)/configure
	sed -i -e 's/#XZ_SUPPORT = 1/XZ_SUPPORT = 1/' \
	-e 's/#LZMA_XZ_SUPPORT = .*/LZMA_XZ_SUPPORT = 1/' \
	-e 's/INSTALL_DIR/DESTDIR/' \
	$(SQUASHFS_DIR)/$(SQUASHFS_SUBDIR)/Makefile
	touch $@
endif

ifeq ($(BR2_PACKAGE_SQUASHFS_HOST),y)
SQUASHFS_HOST_DEPENDENCIES = uclibc xz-host zlib-host
SQUASHFS_HOST_MAKE_OPT = EXTRA_LDFLAGS="$(HOST_LDFLAGS) $(HOST_RPATH)" \
	EXTRA_CFLAGS="$(HOST_CFLAGS)" CC="$(HOSTCC)"
SQUASHFS_HOST_INSTALL_OPT = DESTDIR=$(HOST_DIR)/usr/bin install

$(eval $(call AUTOTARGETS_HOST,package,squashfs))

$(SQUASHFS_HOST_HOOK_POST_EXTRACT):
	echo -e "#!/bin/sh\ntrue" > $(SQUASHFS_HOST_DIR)/$(SQUASHFS_SUBDIR)/configure
	chmod +x $(SQUASHFS_HOST_DIR)/$(SQUASHFS_SUBDIR)/configure
	sed -i -e 's/#XZ_SUPPORT = 1/XZ_SUPPORT = 1/' \
	-e 's/#LZMA_XZ_SUPPORT = .*/LZMA_XZ_SUPPORT = 1/' \
	-e 's/INSTALL_DIR/DESTDIR/' \
	$(SQUASHFS_HOST_DIR)/$(SQUASHFS_SUBDIR)/Makefile
	touch $@
endif
