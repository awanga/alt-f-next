#############################################################
#
# samba-small
#
#############################################################

# this is a stripped-down version of samba, to fit the available dns-323 flash memory space
# see notes in packages/samba/samba.mk

SAMBA_SMALL_VERSION:=3.5.22

ifeq ($(SAMBA_SMALL_VERSION),3.3.9)
	SAMBA_SMALL_SUBDIR=source
else
	SAMBA_SMALL_SUBDIR=source3
endif

SAMBA_SMALL_SOURCE:=samba-$(SAMBA_SMALL_VERSION).tar.gz
SAMBA_SMALL_DIRM:=$(BUILD_DIR)/samba-small-$(SAMBA_SMALL_VERSION)
SAMBA_SMALL_DIR:=$(SAMBA_SMALL_DIRM)/$(SAMBA_SMALL_SUBDIR)
SAMBA_SMALL_DEPS = mklibs-host popt libiconv zlib
SAMBA_SMALL_CAT:=$(ZCAT)
SAMBA_SMALL_TARGET_BINARY:=usr/sbin/smbd

# specific compiler optimization
SAMBA_SMALL_CFLAGS = CFLAGS="$(TARGET_CFLAGS)"
ifneq ($(BR2_PACKAGE_SAMBA_SMALL_OPTIM),)
	SAMBA_SMALL_CFLAGS = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_SAMBA_SMALL_OPTIM)"
endif

$(DL_DIR)/$(SAMBA_SMALL_SOURCE): $(DL_DIR)/$(SAMBA_SOURCE)

$(SAMBA_SMALL_DIR)/.unpacked: $(DL_DIR)/$(SAMBA_SMALL_SOURCE)
	mkdir -p $(SAMBA_SMALL_DIRM)
	$(SAMBA_SMALL_CAT) $(DL_DIR)/$(SAMBA_SMALL_SOURCE) | tar --strip-components=1 -C  $(SAMBA_SMALL_DIRM) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh `dirname $(SAMBA_SMALL_DIR)` package/samba/ samba-$(SAMBA_SMALL_VERSION)-\*.patch
	$(CONFIG_UPDATE) $(SAMBA_SMALL_DIR)
	touch $@

$(SAMBA_SMALL_DIR)/.configured: $(SAMBA_SMALL_DIR)/.unpacked
	(cd $(SAMBA_SMALL_DIR); rm -rf config.cache; \
		./autogen.sh; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		$(SAMBA_SMALL_CFLAGS) $(SAMBA_SMALL_LIBS) \
		samba_cv_HAVE_GETTIMEOFDAY_TZ=yes \
		samba_cv_USE_SETREUID=yes \
		samba_cv_HAVE_KERNEL_OPLOCKS_LINUX=yes \
		libreplace_cv_HAVE_IFACE_IFCONF=yes \
		libreplace_cv_HAVE_MMAP=yes \
		samba_cv_HAVE_FCNTL_LOCK=yes \
		libreplace_cv_HAVE_SECURE_MKSTEMP=yes \
		samba_cv_CC_NEGATIVE_ENUM_VALUES=yes \
		samba_cv_fpie=no \
		samba_cv_have_longlong=yes \
		ac_cv_file__proc_sys_kernel_core_pattern=yes \
		libreplace_cv_HAVE_GETADDRINFO_BUG=no \
		libreplace_cv_HAVE_IPV6=$(if $(BR2_INET_IPV6),yes,no) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--localstatedir=/var \
		--libdir=/usr/lib \
		--with-lockdir=/var/cache/samba \
		--with-piddir=/var/run \
		--with-privatedir=/etc/samba \
		--with-logfilebase=/var/log/samba \
		--with-configdir=/etc/samba \
		--with-libiconv=$(STAGING_DIR)/usr \
		--with-cifsumount \
		--without-acl-support \
		--without-ldap \
		--without-ads \
		--without-winbind \
		--without-included-popt \
		--without-cluster-support \
		--without-dmapi \
		--without-pam \
		--disable-netapi \
		--with-included-iniparser \
		--enable-shared-libs \
		--disable-cups --disable-avahi \
		$(DISABLE_LARGEFILE) \
	)
	touch $@

$(SAMBA_SMALL_DIR)/.mkcommon : $(SAMBA_SMALL_DIR)/.configured
	patch -p0 -b -d $(SAMBA_SMALL_DIR) < package/samba/samba-$(SAMBA_SMALL_VERSION)-Makefile.patch2
	sed -i 's/-Wl,--as-needed//' $(SAMBA_SMALL_DIR)/Makefile
	touch $@

$(SAMBA_SMALL_DIR)/.build: $(SAMBA_SMALL_DIR)/.mkcommon
	echo SAMBA_SMALL_CFLAGS=$(SAMBA_SMALL_CFLAGS)
	# make proto must be done before make to be parallel safe
	$(MAKE) -C $(SAMBA_SMALL_DIR) proto
	$(MAKE) -C $(SAMBA_SMALL_DIR)
	(cd $(SAMBA_SMALL_DIR)/bin; \
	mkdir -p tmp; rm -f tmp/*; \
	mklibs -v -D -d tmp/ \
	--target arm-linux-uclibcgnueabi \
	-L .:$(TARGET_DIR)/lib:$(TARGET_DIR)/usr/lib \
	--ldlib $(TARGET_DIR)/lib/ld-uClibc.so.0 \
	smbd nmbd smbtree smbstatus swat smbpasswd; \
	cp tmp/libsmbcommon.so libsmbcommon.so; \
	)
	touch $@

SAMBA_SMALL_TARGETS_y = usr/lib/libsmbcommon.so \
	usr/bin/smbpasswd usr/bin/smbstatus usr/bin/smbtree \
	usr/sbin/mount.cifs usr/sbin/umount.cifs \
	usr/sbin/nmbd usr/sbin/smbd usr/sbin/swat

SAMBA_SMALL_TARGETS_ = usr/bin/sharesec usr/bin/eventlogadm \
	usr/bin/net usr/bin/nmblookup usr/bin/ntlm_auth \
	usr/bin/pdbedit usr/bin/profiles usr/bin/rpcclient \
	usr/bin/smbcacls usr/bin/smbclient usr/bin/smbcontrol \
	usr/bin/smbcquotas usr/bin/smbget usr/bin/smbspool \
	usr/bin/smbtar usr/bin/tdbbackup usr/bin/tdbdump \
	usr/bin/tdbtool usr/bin/testparm usr/sbin/winbindd \
	usr/bin/wbinfo usr/bin/findsmb

SAMBA_SMALL_INSTALL_TARGETS = installlibs installservers installbin \
	installcifsmount installcifsumount installscripts

#$(SAMBA_SMALL_DIR)/.installed: $(SAMBA_SMALL_DIR)/.build
$(PROJECT_BUILD_DIR)/autotools-stamps/samba-small_target_installed: $(SAMBA_SMALL_DIR)/.build
	$(MAKE) $(TARGET_CONFIGURE_OPTS) \
		prefix="${TARGET_DIR}/usr" \
		BASEDIR="${TARGET_DIR}/usr" \
		SBINDIR="${TARGET_DIR}/usr/sbin" \
		LOCKDIR="${TARGET_DIR}/var/cache/samba" \
		PRIVATEDIR="${TARGET_DIR}/etc/samba" \
		CONFIGDIR="${TARGET_DIR}/etc/samba" \
		VARDIR="${TARGET_DIR}/var/log/samba" \
		MODULESDIR="${TARGET_DIR}/usr/lib" \
		LIBDIR="${TARGET_DIR}/usr/lib" \
		-C $(SAMBA_SMALL_DIR) $(SAMBA_SMALL_INSTALL_TARGETS)
	# jc: 	
	-cp $(SAMBA_SMALL_DIR)/bin/libsmbcommon.so $(TARGET_DIR)/usr/lib/
	-chmod +w $(TARGET_DIR)/usr/lib/libsmbcommon.so
	# Do not install the LDAP-like embedded database tools
	rm -f $(addprefix $(TARGET_DIR)/usr/bin/ldb, add del edit modify rename search)
	# Remove not used library by Samba binaries
	( cd $(TARGET_DIR)/usr/lib; \
	rm -f libnetapi* libsmbclient* libtalloc* \
	libtdb* libwbclient* libsmbsharemodes* \
	)
	# Remove not wanted Samba binaries
	for file in $(SAMBA_SMALL_TARGETS_); do \
		rm -f $(TARGET_DIR)/$$file; \
	done
	# Strip the wanted Samba binaries
	for file in $(SAMBA_SMALL_TARGETS_y); do \
		$(STRIPCMD) $(STRIP_STRIP_ALL) $(TARGET_DIR)/$$file; \
	done
	cp -dpfr $(SAMBA_SMALL_DIR)/../swat $(TARGET_DIR)/usr/
	rm -rf $(TARGET_DIR)/var/cache/samba
	rm -rf $(TARGET_DIR)/var/lib/samba
	find $(TARGET_DIR) -name \*.old -delete
	touch $@

samba-small: $(SAMBA_SMALL_DEPS) $(PROJECT_BUILD_DIR)/autotools-stamps/samba-small_target_installed

samba-small-build: $(SAMBA_SMALL_DIR)/.build

samba-small-configure: $(SAMBA_SMALL_DIR)/.configured

samba-small-unpacked: $(SAMBA_SMALL_DIR)/.unpacked

samba-small-source: $(DL_DIR)/$(SAMBA_SMALL_SOURCE)

samba-small-clean:
	-$(MAKE) -C $(SAMBA_SMALL_DIR) clean
	rm -f $(SAMBA_SMALL_DIR)/.build
	
samba-small-uninstall:
	-$(MAKE)  $(TARGET_CONFIGURE_OPTS) \
		prefix="${TARGET_DIR}/usr" \
		BASEDIR="${TARGET_DIR}/usr" \
		SBINDIR="${TARGET_DIR}/usr/sbin" \
		LOCKDIR="${TARGET_DIR}/var/cache/samba" \
		PRIVATEDIR="${TARGET_DIR}/etc/samba" \
		CONFIGDIR="${TARGET_DIR}/etc/samba" \
		VARDIR="${TARGET_DIR}/var/log/samba" \
		MODULESDIR="${TARGET_DIR}/usr/lib" \
		LIBDIR="${TARGET_DIR}/usr/lib" \
		-C $(SAMBA_SMALL_DIR) uninstall
	rm -f $(TARGET_DIR)/usr/lib/libsmbcommon.so
	rm -f $(TARGET_DIR)/etc/init.d/S91smb
	rm -rf $(TARGET_DIR)/etc/samba
	rm -f $(SAMBA_SMALL_DIR)/.installed

samba-small-dirclean: samba-small-uninstall
	rm -rf $(SAMBA_SMALL_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
#ifeq ($(BR2_PACKAGE_SAMBA_SMALL),y)
#TARGETS+=samba-small
#endif
