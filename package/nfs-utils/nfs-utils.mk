#############################################################
#
# nfs-utils
#
#############################################################

NFS_UTILS_VERSION:=1.3.3
NFS_UTILS_SOURCE:=nfs-utils-$(NFS_UTILS_VERSION).tar.bz2
NFS_UTILS_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/nfs/nfs-utils/$(NFS_UTILS_VERSION)

NFS_UTILS_CAT:=$(BZCAT)
NFS_UTILS_DIR:=$(BUILD_DIR)/nfs-utils-$(NFS_UTILS_VERSION)
NFS_UTILS_BINARY:=utils/nfsd/nfsd
NFS_UTILS_TARGET_BINARY:=usr/sbin/rpc.nfsd

BR2_NFS_UTILS_CFLAGS=

ifeq ($(BR2_LARGEFILE),)
BR2_NFS_UTILS_CFLAGS+=-U_LARGEFILE64_SOURCE -U_FILE_OFFSET_BITS
endif

BR2_NFS_UTILS_CFLAGS+=-DUTS_RELEASE='\"$(LINUX_HEADERS_VERSION)\"'

$(DL_DIR)/$(NFS_UTILS_SOURCE):
	 $(call DOWNLOAD,$(NFS_UTILS_SITE),$(NFS_UTILS_SOURCE))

$(NFS_UTILS_DIR)/.unpacked: $(DL_DIR)/$(NFS_UTILS_SOURCE)
	$(NFS_UTILS_CAT) $(DL_DIR)/$(NFS_UTILS_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(NFS_UTILS_DIR) package/nfs-utils/ nfs-utils-$(NFS_UTILS_VERSION)\*.patch
	(cd $(NFS_UTILS_DIR); autoconf)
	$(CONFIG_UPDATE) $(NFS_UTILS_DIR)
	touch $@

$(NFS_UTILS_DIR)/.configured: $(NFS_UTILS_DIR)/.unpacked
	(cd $(NFS_UTILS_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		CFLAGS="$(TARGET_CFLAGS) $(BR2_NFS_UTILS_CFLAGS)" \
		CONFIG_SQLITE3_FALSE='#' CONFIG_NFSDCLD_FALSE='#' \
		knfsd_cv_bsd_signals=no \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--without-tcp-wrappers \
		--without-krb5 \
		--disable-uuid \
		--disable-nfsv4 \
		--disable-nfsv41 \
		--disable-gss \
		--disable-tirpc \
		--disable-static \
		--disable-ipv6 \
	)
	touch $@

$(NFS_UTILS_DIR)/$(NFS_UTILS_BINARY): $(NFS_UTILS_DIR)/.configured
	$(MAKE) CC=$(TARGET_CC) CC_FOR_BUILD="$(HOSTCC)" \
		RPCGEN=/usr/bin/rpcgen -C $(NFS_UTILS_DIR)
	touch -c $@

NFS_UTILS_TARGETS_ := usr/sbin/mount.nfs4 usr/sbin/umount.nfs4 	\
	usr/sbin/nfsiostat usr/sbin/mountstats usr/sbin/nfsstat
NFS_UTILS_TARGETS_y := usr/sbin/exportfs usr/sbin/rpc.mountd \
	usr/sbin/rpc.nfsd usr/sbin/rpc.statd usr/sbin/sm-notify

NFS_UTILS_TARGETS_$(BR2_PACKAGE_NFS_UTILS_RPCDEBUG) += usr/sbin/rpcdebug
NFS_UTILS_TARGETS_$(BR2_PACKAGE_NFS_UTILS_RPC_LOCKD) += usr/sbin/rpc.lockd
# nfs-utils-1.2.7/NEWS: - rpc.rquotad is gone.  Use the one from the 'quota' package
#NFS_UTILS_TARGETS_$(BR2_PACKAGE_NFS_UTILS_RPC_RQUOTAD) += usr/sbin/rpc.rquotad

$(PROJECT_BUILD_DIR)/.fakeroot.nfs-utils: $(NFS_UTILS_DIR)/$(NFS_UTILS_BINARY)
	# Use fakeroot to pretend to do 'make install' as root
	echo '$(MAKE) $(TARGET_CONFIGURE_OPTS) RPCGEN=/usr/bin/rpcgen prefix=$(TARGET_DIR)/usr statedir=$(TARGET_DIR)/var/lib/nfs statdpath=$(TARGET_DIR)/var/lib/nfs sbindir=$(TARGET_DIR)/usr/sbin -C $(NFS_UTILS_DIR) install-strip' > $@
	echo 'rm -f $(TARGET_DIR)/usr/bin/event_rpcgen.py $(TARGET_DIR)/usr/sbin/nhfs*' >> $@
	echo 'rm -rf $(TARGET_DIR)/usr/share/man' >> $@
	echo -n 'for file in $(NFS_UTILS_TARGETS_); do rm -f $(TARGET_DIR)/' >> $@
	echo -n "\$$" >> $@
	echo "file; done" >> $@
	echo 'rm -rf $(TARGET_DIR)/var/lib' >> $@

$(TARGET_DIR)/$(NFS_UTILS_TARGET_BINARY): $(PROJECT_BUILD_DIR)/.fakeroot.nfs-utils
	touch  $@

nfs-utils-source: $(DL_DIR)/$(NFS_UTILS_SOURCE)

nfs-utils-configure: $(NFS_UTILS_DIR)/.configured

nfs-utils-build: $(NFS_UTILS_DIR)/$(NFS_UTILS_BINARY)

nfs-utils: uclibc host-autoconf host-fakeroot $(TARGET_DIR)/$(NFS_UTILS_TARGET_BINARY)

nfs-utils-uninstall:
	$(MAKE) -i DESTDIR=$(TARGET_DIR) -C $(NFS_UTILS_DIR) uninstall

nfs-utils-clean:
	rm -f $(TARGET_DIR)/etc/init.d/S60nfs
	for file in $(NFS_UTILS_TARGETS_y); do \
		rm -f $(TARGET_DIR)/$$file; \
	done
	-$(MAKE) -C $(NFS_UTILS_DIR) clean
	rm -f $(PROJECT_BUILD_DIR)/.fakeroot.nfs-utils

nfs-utils-dirclean:
	rm -rf $(NFS_UTILS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_NFS_UTILS),y)
TARGETS+=nfs-utils
endif
