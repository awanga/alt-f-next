#############################################################
#
# btrfs-progs
#
#############################################################

BTRFS_PROGS_VERSION = 4.5.3
BTRFS_PROGS_SOURCE = btrfs-progs-v$(BTRFS_PROGS_VERSION).tar.xz
BTRFS_PROGS_SITE = $(BR2_KERNEL_MIRROR)/linux/kernel/people/kdave/btrfs-progs

BTRFS_PROGS_INSTALL_STAGING = NO
BTRFS_PROGS_INSTALL_TARGET = YES
BTRFS_PROGS_DEPENDENCIES = uclibc attr acl zlib lzo e2fsprogs util-linux

BTRFS_PROGS_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

BTRFS_PROGS_OPTI=-I$(BTRFS_PROGS_DIR)/util-linux/include/
BTRFS_PROGS_OPTL=-L$(BTRFS_PROGS_DIR)/util-linux/lib/

BTRFS_PROGS_CONF_OPT = --disable-backtrace --disable-documentation
BTRFS_PROGS_CONF_ENV = ZLIB_CFLAGS=" " ZLIB_LIBS="-lz" \
	BLKID_CFLAGS="$(BTRFS_PROGS_OPTI)" \
	BLKID_LIBS="$(BTRFS_PROGS_OPTL)  -lblkid" \
	UUID_CFLAGS=$(BTRFS_PROGS_OPTI) \
	UUID_LIBS="$(BTRFS_PROGS_OPTL)  -luuid" \
	CC="$(TARGET_CC) $(BTRFS_PROGS_OPTI) $(TARGET_CFLAGS)" \
	LDFLAGS="$(BTRFS_PROGS_OPTL) $(TARGET_LDFLAGS)" 

$(eval $(call AUTOTARGETS,package,btrfs-progs))
