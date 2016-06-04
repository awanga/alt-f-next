#############################################################
#
# util-linux
#
#############################################################

# this "package" is intended to only provide a recent static libblkid and libuuid for the btrfs-progs package
# The libs and includes are installed in the btrfs-progs build dir, and not installed in the target or staging dir

UTIL-LINUX_VERSION:=2.27.1
UTIL-LINUX_SOURCE:=util-linux-$(UTIL-LINUX_VERSION).tar.xz
UTIL-LINUX_SITE:=$(BR2_KERNEL_MIRROR)/linux/utils/util-linux/v$(UTIL-LINUX_VERSION)

UTIL-LINUX_DIR:=$(BUILD_DIR)/util-linux-$(UTIL-LINUX_VERSION)
UTIL-LINUX_CAT:=$(XZCAT)

UTIL-LINUX_BINARY:=$(UTIL-LINUX_DIR)/misc-utils/chkdupexe
UTIL-LINUX_TARGET_BINARY:=$(BTRFS_PROGS_DIR)/util-linux/lib/libblkid.a

# schedutils isn't support for all archs
ifneq ($(BR2_i386)$(BR2_powerpc)$(BR2_x86_64)$(BR2_ia64)$(BR2_alpha),)
UTIL-LINUX_SCHED_UTILS:=--enable-schedutils
else
UTIL-LINUX_SCHED_UTILS:=--disable-schedutils
endif

ifeq ($(BR2_PACKAGE_LIBINTL),y)
UTIL-LINUX_DEPENDENCIES += libintl
UTIL-LINUX_MAKE_OPT = LIBS=-lintl
endif

$(DL_DIR)/$(UTIL-LINUX_SOURCE):
	$(call DOWNLOAD,$(UTIL-LINUX_SITE),$(UTIL-LINUX_SOURCE))

$(UTIL-LINUX_DIR)/.unpacked: $(DL_DIR)/$(UTIL-LINUX_SOURCE)
	$(UTIL-LINUX_CAT) $(DL_DIR)/$(UTIL-LINUX_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(UTIL-LINUX_DIR) package/util-linux/ util-linux\*.patch
	touch $(UTIL-LINUX_DIR)/.unpacked

# build for btrfs only, as it needs recent libblkid/libuuid
# build as static libs, to not conflict with e2fsprogs versions
$(UTIL-LINUX_DIR)/.configured: $(UTIL-LINUX_DIR)/.unpacked
	(cd $(UTIL-LINUX_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		CFLAGS="$(TARGET_CFLAGS)"  \
		ac_cv_lib_blkid_blkid_known_fstype=no \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--disable-use-tty-group \
		--prefix=/ \
		--exec-prefix=/ \
		--sysconfdir=/etc \
		--datadir=/usr/share \
		--localstatedir=/var \
		--mandir=/usr/man \
		--infodir=/usr/info \
		$(UTIL-LINUX_SCHED_UTILS) \
		$(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
		ARCH=$(ARCH) \
		--disable-shared --enable-static --disable-all-programs --enable-libblkid -enable-libuuid \
	)
	touch $(UTIL-LINUX_DIR)/.configured

$(UTIL-LINUX_BINARY): $(UTIL-LINUX_DIR)/.configured
	$(MAKE) \
		-C $(UTIL-LINUX_DIR) \
		ARCH=$(ARCH) \
		CC=$(TARGET_CC) \
		CFLAGS="$(TARGET_CFLAGS)" \
		$(UTIL-LINUX_MAKE_OPT) \
		HAVE_SLANG="NO"

# install for btrfs only, as it needs a recent libblkid
$(UTIL-LINUX_TARGET_BINARY): $(UTIL-LINUX_BINARY)
	$(MAKE) ARCH=$(ARCH) DESTDIR=$(BTRFS_PROGS_DIR)/util-linux USE_TTY_GROUP=no -C $(UTIL-LINUX_DIR) install
	(cd $(BTRFS_PROGS_DIR)/util-linux; rm -rf bin sbin usr)

#If both util-linux and busybox are selected, make certain util-linux
#wins the fight over who gets to have their utils actually installed
ifeq ($(BR2_PACKAGE_BUSYBOX),y)
UTIL-LINUX_DEPENDENCIES := busybox $(UTIL-LINUX_DEPENDENCIES)
endif

util-linux: uclibc $(UTIL-LINUX_DEPENDENCIES) $(UTIL-LINUX_TARGET_BINARY)

util-linux-build: $(UTIL-LINUX_BINARY)

util-linux-configure: $(UTIL-LINUX_DIR)/.configured

util-linux-source: $(DL_DIR)/$(UTIL-LINUX_SOURCE)

util-linux-clean:
	#There is no working 'uninstall' target. Just skip it...
	#$(MAKE) DESTDIR=$(TARGET_DIR) -C $(UTIL-LINUX_DIR) uninstall
	-$(MAKE) -C $(UTIL-LINUX_DIR) clean

util-linux-dirclean:
	rm -rf $(UTIL-LINUX_DIR)


#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_UTIL-LINUX),y)
TARGETS+=util-linux
endif
