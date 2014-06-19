#############################################################
#
# btrfs-progs
#
#############################################################

BTRFS_PROGS_VERSION = v3.14.2
BTRFS_PROGS_SOURCE = btrfs-progs-$(BTRFS_PROGS_VERSION).tar.xz
BTRFS_PROGS_SITE = https://www.kernel.org/pub/linux/kernel/people/mason/btrfs-progs

BTRFS_PROGS_INSTALL_STAGING = NO
BTRFS_PROGS_INSTALL_TARGET = YES
BTRFS_PROGS_DEPENDENCIES = uclibc attr acl zlib lzo e2fsprogs

BTRFS_PROGS_MAKE_ENV = $(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ENV)

$(eval $(call AUTOTARGETS,package,btrfs-progs))

$(BTRFS_PROGS_TARGET_CONFIGURE):
	touch $@

$(BTRFS_PROGS_HOOK_POST_CONFIGURE):
	$(SED) 's/build-Documentation//' -e 's/install-Documentation//' \
		-e 's/^CC = .*//' -e 's/^CFLAGS = .*//' $(BTRFS_PROGS_DIR)/Makefile
	touch $@
