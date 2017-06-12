#############################################################
#
# samba
#
############################################################

# uClibc must be compiled with UCLIBC_SUPPORT_AI_ADDRCONFIG, or else an
# "interface" option must be specified in the samba config.file
# (or an "couln'd get interface address" (or similar) error happens at runtime 

SAMBA36_VERSION:=3.6.25-
SAMBA36_SUBDIR=source3

SAMBA36_SOURCE:=samba-$(SAMBA36_VERSION).tar.gz
SAMBA36_SITE:=http://samba.org/samba/ftp/stable/
SAMBA36_DIR:=$(BUILD_DIR)/samba-$(SAMBA36_VERSION)/$(SAMBA36_SUBDIR)
SAMBA36_DEPS =  popt libiconv 
SAMBA36_CAT:=$(ZCAT)
SAMBA36_BINARY:=bin/samba_multicall-
SAMBA36_TARGET_BINARY:=usr/sbin/nmbd-

ifeq ($(BR2_PACKAGE_SAMBA36_SMALL),y)
	SAMBA36_MODE= $(SAMBA36_DIR)/.small
	SAMBA36_BUILD_TARGET = basics libs $(SAMBA36_BINARY)
	SAMBA36_ACL=--without-acl-support
else
	SAMBA36_MODE= $(SAMBA36_DIR)/.large
ifeq ($(BR2_PACKAGE_ACL),y)
	SAMBA36_ACL = --with-acl-support
	SAMBA36_DEPS += acl
	SAMBA36_LIBS = LIBS="-lacl -lintl"
endif
endif


# specific package compiler optimization
# Optim Free
# -O0: -303 KB
# -O:    40 KB
# -O1:   36 KB
# -Os:    4 KB
# -O2: -102 KB
# -O3: -168 KB
# specific compiler optimization
SAMBA36_CFLAGS = CFLAGS="$(TARGET_CFLAGS)"
ifneq ($(BR2_PACKAGE_SAMBA36_OPTIM),)
	SAMBA36_CFLAGS = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_SAMBA36_OPTIM)"
endif

$(DL_DIR)/$(SAMBA36_SOURCE):
	$(call DOWNLOAD,$(SAMBA36_SITE),$(SAMBA36_SOURCE))

$(SAMBA36_DIR)/.unpacked: $(DL_DIR)/$(SAMBA36_SOURCE)
	$(SAMBA36_CAT) $(DL_DIR)/$(SAMBA36_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh `dirname $(SAMBA36_DIR)` package/samba36/ samba-$(SAMBA36_VERSION)-\*.patch
	$(CONFIG_UPDATE) $(SAMBA36_DIR)
	touch $@

# not all entware patches are used, as they remove printer and Windows Vista Backup support.
# if all patch were apllied a further ~1.2MB would be saved (7.3MB vs 8.5MB)
# some entware patches define the following:
#PRINTER_SUPPORT needed
#LSA_SUPPORT needed
#NETLOGON_SUPPORT
#DFS_SUPPORT 
#SAMR_SUPPORT 
#SRVSVC_SUPPORT 
#WINREG_SUPPORT 

$(SAMBA36_MODE):
	if test -f $(SAMBA36_DIR)/.small -a $(SAMBA36_MODE) != $(SAMBA36_DIR)/.small; then \
		$(MAKE)  samba36-clean; \
		rm -f $(SAMBA36_DIR)/.configured $(SAMBA36_DIR)/.small; \
	elif test -f $(SAMBA36_DIR)/.large -a $(SAMBA36_MODE) != $(SAMBA36_DIR)/.large; then \
		$(MAKE) samba36-clean; \
		rm -f $(SAMBA36_DIR)/.configured $(SAMBA36_DIR)/.large; \
	else \
		rm -f $(SAMBA36_DIR)/{.large,.small}; \
	fi
	touch $@

$(SAMBA36_DIR)/.configured: $(SAMBA36_DIR)/.unpacked $(SAMBA36_MODE)
	(cd $(SAMBA36_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		$(SAMBA36_CFLAGS) $(SAMBA36_LIBS) \
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
		libreplace_cv_HAVE_GETADDRINFO=yes \
		libreplace_cv_HAVE_IPV6=$(if $(BR2_INET_IPV6),yes,no) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--localstatedir=/var \
		--libdir=/usr/lib \
		--with-modulesdir=/usr/lib/samba \
		--with-codepagedir=/usr/lib/samba \
		--with-lockdir=/var/cache/samba \
		--with-piddir=/var/run \
		--with-logfilebase=/var/log/samba \
		--with-nmbdsocketdir=/var/run/samba \
		--with-ncalrpcdir=/var/run/samba \
		--with-privatedir=/etc/samba \
		--with-configdir=/etc/samba \
		--with-libiconv=$(STAGING_DIR)/usr \
		--with-sendfile-support \
		--disable-static \
		--disable-shared-libs \
		--disable-cups \
		--disable-avahi \
		--without-krb5 \
		--without-libtdb \
		--without-libtalloc \
		--without-libsmbclient \
		--without-libsmbsharemodes \
		--without-libtevent \
		--without-libaddns \
		--without-ldap \
		--without-ads \
		--without-winbind \
		--without-included-popt \
		--without-cluster-support \
		--without-dmapi \
		--without-pam \
		--without-libnetapi \
		--with-included-iniparser \
		$(SAMBA36_ACL) \
		$(DISABLE_LARGEFILE) \
	)
	touch $@

# entware-ng uses also --with-shared-modules=\
#pdb_tdbsam,pdb_wbc_sam,idmap_nss,nss_info_template,auth_winbind,auth_wbc,auth_domain
#		--with-shared-modules="" \

# the default builtin modules (smbd -b) are:
# pdb_smbpasswd pdb_tdbsam pdb_wbc_sam idmap_tdb idmap_passdb idmap_nss nss_info_template auth_sam auth_unix auth_winbind auth_wbc auth_server auth_domain auth_builtin vfs_default
# --with-static-modules="" \

$(SAMBA36_DIR)/$(SAMBA36_BINARY): $(SAMBA36_DIR)/.configured
	# make proto must be done before make to be parallel safe
	$(MAKE) -C $(SAMBA36_DIR) proto
	$(MAKE) -C $(SAMBA36_DIR) $(SAMBA36_BUILD_TARGET)
	touch $@

SAMBA36_TARGETS_ := 

SAMBA36_TARGETS_y := usr/sbin/smbd  usr/sbin/nmbd usr/bin/smbpasswd \
	usr/bin/smbstatus usr/bin/smbtree usr/sbin/swat

ifeq ($(BR2_PACKAGE_SAMBA36_SMALL),y)
SAMBA36_TARGETS_y += usr/sbin/samba_multicall
endif

# findsmb depends on perl, smbtar depends on smbclient
ifeq ($(BR2_PACKAGE_SAMBA36_EXTRA),y)
SAMBA36_TARGETS_y += /usr/bin/smbta-util 
SAMBA36_TARGETS_y += /usr/bin/sharesec
SAMBA36_TARGETS_y += usr/bin/eventlogadm
SAMBA36_TARGETS_y += usr/bin/findsmb
SAMBA36_TARGETS_y += usr/bin/net
SAMBA36_TARGETS_y += usr/bin/nmblookup
SAMBA36_TARGETS_y += usr/bin/ntlm_auth
SAMBA36_TARGETS_y += usr/bin/pdbedit
SAMBA36_TARGETS_y += usr/bin/profiles
SAMBA36_TARGETS_y += usr/bin/rpcclient
SAMBA36_TARGETS_y += usr/bin/smbcacls
SAMBA36_TARGETS_y += usr/bin/smbclient
SAMBA36_TARGETS_y += usr/bin/smbcontrol
SAMBA36_TARGETS_y += usr/bin/smbcquotas
SAMBA36_TARGETS_y += usr/bin/smbget
SAMBA36_TARGETS_y += usr/bin/smbspool
SAMBA36_TARGETS_y += usr/bin/smbtar
SAMBA36_TARGETS_y += usr/bin/tdbbackup usr/bin/tdbdump usr/bin/tdbtool /usr/bin/tdbrestore
SAMBA36_TARGETS_y += usr/bin/testparm
# cifs-utils: SAMBA36_TARGETS_y += usr/sbin/mount.cifs usr/sbin/umount.cifs
# ldb-tools: SAMBA36_TARGETS_y += usr/bin/ldbsearch usr/bin/ldbedit usr/bin/ldbmodify \
#					usr/bin/ldbadd usr/bin/ldbrename usr/bin/ldbdel
# --without-winbind  SAMBA36_TARGETS_y += usr/sbin/winbindd usr/bin/wbinfo
endif

SAMBA36_INSTALL_TARGETS :=

ifeq ($(BR2_PACKAGE_SAMBA36_SMALL),y)
SAMBA36_INSTALL_TARGETS += installlibs
endif

ifeq ($(BR2_PACKAGE_SAMBA36_EXTRA),y)
SAMBA36_INSTALL_TARGETS += installscripts installbin
endif

ifeq ($(BR2_PACKAGE_SAMBA36_DOC),y)
SAMBA36_INSTALL_TARGETS += installswat
endif

ifeq ($(BR2_PACKAGE_SAMBA36_MODULES),y)
SAMBA36_INSTALL_TARGETS += installmodules
endif

$(TARGET_DIR)/$(SAMBA36_TARGET_BINARY): $(SAMBA36_DIR)/$(SAMBA36_BINARY)
	$(MAKE) $(TARGET_CONFIGURE_OPTS) \
		prefix="${TARGET_DIR}/usr" \
		BASEDIR="${TARGET_DIR}/usr" \
		SBINDIR="${TARGET_DIR}/usr/sbin" \
		LOCKDIR="${TARGET_DIR}/var/cache/samba" \
		PRIVATEDIR="${TARGET_DIR}/etc/samba" \
		CONFIGDIR="${TARGET_DIR}/etc/samba" \
		VARDIR="${TARGET_DIR}/var/log/samba" \
		MODULESDIR="${TARGET_DIR}/usr/lib/samba" \
		CODEPAGEDIR="${TARGET_DIR}/usr/lib/samba" \
		LIBDIR="${TARGET_DIR}/usr/lib" \
		-C $(SAMBA36_DIR) $(SAMBA36_INSTALL_TARGETS)
ifeq ($(BR2_PACKAGE_SAMBA36_DOC),y)
#	cp -dpfr $(SAMBA36_DIR)/../swat $(TARGET_DIR)/usr/
	cp -dpfr $(SAMBA36_DIR)/../swat/help/welcome.html $(TARGET_DIR)/usr/swat/help/
#	rm -rf $(TARGET_DIR)/usr/swat/lang
endif
	cp $(SAMBA36_DIR)/bin/samba_multicall "${TARGET_DIR}"/usr/sbin
	(cd "${TARGET_DIR}"/usr/sbin ; \
	ln -sf samba_multicall smbd ;\
	ln -sf samba_multicall nmbd ;\
	ln -sf samba_multicall swat ;\
	cd ../bin ;\
	ln -sf ../sbin/samba_multicall smbstatus ;\
	ln -sf ../sbin/samba_multicall smbtree ;\
	ln -sf ../sbin/samba_multicall smbpasswd ;\
	)
#ifneq ($(BR2_PACKAGE_SAMBA36_EXTRA),y)
	# Do not install the LDAP-like embedded database tools
	##rm -f $(addprefix $(TARGET_DIR)/usr/bin/ldb, add del edit modify rename search)
#endif
	# Remove not used library by Samba binaries
	##rm -f $(TARGET_DIR)/usr/lib/libnetapi*
	##rm -f $(TARGET_DIR)/usr/lib/libsmbclient*
	##rm -f $(TARGET_DIR)/usr/lib/libtalloc*
	##rm -f $(TARGET_DIR)/usr/lib/libtdb*
	##rm -f $(TARGET_DIR)/usr/lib/libwbclient*
	##rm -f $(TARGET_DIR)/usr/lib/libsmbsharemodes*
	# Remove not wanted Samba binaries
	#for file in $(SAMBA36_TARGETS_); do \
	#	rm -f $(TARGET_DIR)/$$file; \
	#done
	# Strip the wanted Samba binaries
	#for file in $(SAMBA36_TARGETS_y); do \
	#	$(STRIPCMD) $(STRIP_STRIP_ALL) $(TARGET_DIR)/$$file; \
	#done
#ifeq ($(BR2_PACKAGE_SAMBA36_DOC),y)
	cp -dpfr $(SAMBA36_DIR)/../swat $(TARGET_DIR)/usr/
	rm -rf $(TARGET_DIR)/usr/swat/lang
#endif
	#$(INSTALL) -m 0755 package/samba/S91smb $(TARGET_DIR)/etc/init.d
	#@if [ ! -f $(TARGET_DIR)/etc/samba/smb.conf ]; then \
	#	$(INSTALL) -m 0755 -D package/samba/simple.conf $(TARGET_DIR)/etc/samba/smb.conf; \
	#fi
	#rm -rf $(TARGET_DIR)/var/cache/samba
	#rm -rf $(TARGET_DIR)/var/lib/samba
	find $(TARGET_DIR) -name \*.old -delete

samba36: $(SAMBA36_DEPS) $(TARGET_DIR)/$(SAMBA36_TARGET_BINARY) 

samba36-build: $(SAMBA36_DIR)/$(SAMBA36_BINARY)

samba36-configure: $(SAMBA36_DIR)/.configured

samba36-source: $(DL_DIR)/$(SAMBA36_SOURCE)

samba36-unpacked: $(SAMBA36_DIR)/.unpacked

samba36-clean:
	rm -f $(TARGET_DIR)/$(SAMBA36_TARGET_BINARY)
	for file in $(SAMBA36_TARGETS_y); do \
		rm -f $(TARGET_DIR)/$$file; \
	done
	rm -f $(TARGET_DIR)/etc/init.d/S91smb
	rm -rf $(TARGET_DIR)/etc/samba $(TARGET_DIR)/usr/swat \
		$(TARGET_DIR)/usr/lib/{vfs,auth,charset,idmap,pdb,perfcount}
	-$(MAKE) -C $(SAMBA36_DIR) clean

samba36-dirclean:
	rm -rf $(SAMBA36_DIR)
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_SAMBA36),y)
TARGETS+=samba36
endif
