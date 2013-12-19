#############################################################
#
# samba
#
#############################################################

# uClibc must be compiled with UCLIBC_SUPPORT_AI_ADDRCONFIG, or else an
# "interface" option must be specified in the samba config.file
# (or an "couln'd get interface address" (or similar) error happens at runtime 

#SAMBA_VERSION:=3.3.9
#SAMBA_VERSION:=3.3.15
#SAMBA_VERSION:=3.4.13
#SAMBA_VERSION:=3.5.12
#SAMBA_VERSION:=3.5.15
#SAMBA_VERSION:=3.5.19
SAMBA_VERSION:=3.5.21
#SAMBA_VERSION:=3.6.3 don't fit flash

ifeq ($(SAMBA_VERSION),3.3.9)
	SAMBA_SUBDIR=source
else
	SAMBA_SUBDIR=source3
endif

SAMBA_SOURCE:=samba-$(SAMBA_VERSION).tar.gz
SAMBA_SITE:=http://samba.org/samba/ftp/stable/
SAMBA_DIR:=$(BUILD_DIR)/samba-$(SAMBA_VERSION)/$(SAMBA_SUBDIR)
SAMBA_DEPS = mklibs-host popt libiconv 
SAMBA_CAT:=$(ZCAT)
SAMBA_BINARY:=bin/smbd
SAMBA_TARGET_BINARY:=usr/sbin/smbd

SAMBA_ACL=--without-acl-support
ifeq ($(BR2_PACKAGE_SAMBA_ACL),y)
	SAMBA_ACL = --with-acl-support
	SAMBA_DEPS += acl
	SAMBA_LIBS = LIBS="-lacl -lintl"
endif

# specific compiler optimization
SAMBA_CFLAGS = CFLAGS="$(TARGET_CFLAGS)"
ifneq ($(BR2_PACKAGE_SAMBA_OPTIM),)
	SAMBA_CFLAGS = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_SAMBA_OPTIM)"
endif

# Optim Free
# -O0: -303 KB
# -O:    40 KB
# -O1:   36 KB
# -Os:    4 KB
# -O2: -102 KB
# -O3: -168 KB

$(DL_DIR)/$(SAMBA_SOURCE):
	$(call DOWNLOAD,$(SAMBA_SITE),$(SAMBA_SOURCE))

$(SAMBA_DIR)/.unpacked: $(DL_DIR)/$(SAMBA_SOURCE)
	$(SAMBA_CAT) $(DL_DIR)/$(SAMBA_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh `dirname $(SAMBA_DIR)` package/samba/ samba-$(SAMBA_VERSION)-\*.patch
	$(CONFIG_UPDATE) $(SAMBA_DIR)
	touch $@

$(SAMBA_DIR)/.configured: $(SAMBA_DIR)/.unpacked
	(cd $(SAMBA_DIR); rm -rf config.cache; \
		./autogen.sh; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(TARGET_CONFIGURE_ENV) \
		$(SAMBA_CFLAGS) $(SAMBA_LIBS) \
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
		--without-ldap \
		--without-ads \
		--without-winbind \
		--without-included-popt \
		--without-cluster-support \
		--without-dmapi \
		--without-pam \ \
		--disable-netapi \
		--with-included-iniparser \
		--enable-shared-libs \
		--disable-cups --disable-avahi \
		$(DISABLE_LARGEFILE) \
		$(SAMBA_ACL) \
	)
	touch $@

$(SAMBA_DIR)/$(SAMBA_BINARY): $(SAMBA_DIR)/.configured
	# make proto must be done before make to be parallel safe
	$(MAKE) -C $(SAMBA_DIR) proto
	$(MAKE) -C $(SAMBA_DIR)
	touch $@

SAMBA_TARGETS_ := usr/bin/sharesec
SAMBA_TARGETS_y :=

SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_CIFS) += usr/sbin/mount.cifs usr/sbin/umount.cifs
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_EVENTLOGADM) += usr/bin/eventlogadm
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_FINDSMB) += usr/bin/findsmb
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_NET) += usr/bin/net
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_NMBD) += usr/sbin/nmbd
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_NMBLOOKUP) += usr/bin/nmblookup
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_NTLM_AUTH) += usr/bin/ntlm_auth
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_PDBEDIT) += usr/bin/pdbedit
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_PROFILES) += usr/bin/profiles
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_RPCCLIENT) += usr/bin/rpcclient
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBCACLS) += usr/bin/smbcacls
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBCLIENT) += usr/bin/smbclient
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBCONTROL) += usr/bin/smbcontrol
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBCQUOTAS) += usr/bin/smbcquotas
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBGET) += usr/bin/smbget
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBPASSWD) += usr/bin/smbpasswd
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBSPOOL) += usr/bin/smbspool
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBSTATUS) += usr/bin/smbstatus
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBTAR) += usr/bin/smbtar
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SMBTREE) += usr/bin/smbtree
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_SWAT) += usr/sbin/swat
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_TDB) += usr/bin/tdbbackup \
						   usr/bin/tdbdump \
						   usr/bin/tdbtool
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_TESTPARM) += usr/bin/testparm
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_WINBINDD) += usr/sbin/winbindd
SAMBA_TARGETS_$(BR2_PACKAGE_SAMBA_WBINFO) += usr/bin/wbinfo

SAMBA_INSTALL_TARGETS = installlibs installservers installbin installcifsmount installcifsumount installscripts

ifeq ($(BR2_PACKAGE_SAMBA_DOC),y)
SAMBA_INSTALL_TARGETS += installswat
endif

ifeq ($(BR2_PACKAGE_SAMBA_MODULES),y)
SAMBA_INSTALL_TARGETS += installmodules
endif

# override the above SAMBA_TARGETS. FIXME, remove all those.
# findsmb depends on perl, smbtar depends on smbclient
ifeq ($(BR2_PACKAGE_SAMBA_EXTRA),y)
SAMBA_TARGETS_ := 
SAMBA_TARGETS_y := /usr/bin/net /usr/bin/rpcclient /usr/bin/smbget /usr/bin/smbclient /usr/bin/smbcacls /usr/bin/smbcquotas /usr/bin/smbspool /usr/bin/ntlm_auth /usr/bin/pdbedit /usr/bin/eventlogadm /usr/bin/smbcontrol /usr/bin/nmblookup /usr/bin/ldbsearch /usr/bin/ldbedit /usr/bin/ldbmodify /usr/bin/ldbadd /usr/bin/ldbrename /usr/bin/ldbdel /usr/bin/testparm /usr/bin/sharesec /usr/bin/profiles /usr/bin/tdbtool /usr/bin/tdbbackup /usr/bin/tdbdump
endif

$(TARGET_DIR)/$(SAMBA_TARGET_BINARY): $(SAMBA_DIR)/$(SAMBA_BINARY)
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
		-C $(SAMBA_DIR) $(SAMBA_INSTALL_TARGETS)
ifneq ($(BR2_PACKAGE_SAMBA_EXTRA),y)
	# Do not install the LDAP-like embedded database tools
	rm -f $(addprefix $(TARGET_DIR)/usr/bin/ldb, add del edit modify rename search)
endif
	# Remove not used library by Samba binaries
	rm -f $(TARGET_DIR)/usr/lib/libnetapi*
	rm -f $(TARGET_DIR)/usr/lib/libsmbclient*
	rm -f $(TARGET_DIR)/usr/lib/libtalloc*
	rm -f $(TARGET_DIR)/usr/lib/libtdb*
	rm -f $(TARGET_DIR)/usr/lib/libwbclient*
	rm -f $(TARGET_DIR)/usr/lib/libsmbsharemodes*
	# Remove not wanted Samba binaries
	for file in $(SAMBA_TARGETS_); do \
		rm -f $(TARGET_DIR)/$$file; \
	done
	# Strip the wanted Samba binaries
	$(STRIPCMD) $(STRIP_STRIP_ALL) $(TARGET_DIR)/$(SAMBA_TARGET_BINARY)
	for file in $(SAMBA_TARGETS_y); do \
		$(STRIPCMD) $(STRIP_STRIP_ALL) $(TARGET_DIR)/$$file; \
	done
ifeq ($(BR2_PACKAGE_SAMBA_SWAT),y)
	cp -dpfr $(SAMBA_DIR)/../swat $(TARGET_DIR)/usr/
endif
	#$(INSTALL) -m 0755 package/samba/S91smb $(TARGET_DIR)/etc/init.d
	#@if [ ! -f $(TARGET_DIR)/etc/samba/smb.conf ]; then \
	#	$(INSTALL) -m 0755 -D package/samba/simple.conf $(TARGET_DIR)/etc/samba/smb.conf; \
	#fi
	rm -rf $(TARGET_DIR)/var/cache/samba
	rm -rf $(TARGET_DIR)/var/lib/samba
	find $(TARGET_DIR) -name \*.old -delete # jc:

samba: $(SAMBA_DEPS) $(TARGET_DIR)/$(SAMBA_TARGET_BINARY) 

samba-build: $(SAMBA_DIR)/$(SAMBA_BINARY)

samba-configure: $(SAMBA_DIR)/.configured

samba-source: $(DL_DIR)/$(SAMBA_SOURCE)

samba-unpacked: $(SAMBA_DIR)/.unpacked

samba-clean:
	rm -f $(TARGET_DIR)/$(SAMBA_TARGET_BINARY)
	for file in $(SAMBA_TARGETS_y); do \
		rm -f $(TARGET_DIR)/$$file; \
	done
	rm -f $(TARGET_DIR)/etc/init.d/S91smb
	rm -rf $(TARGET_DIR)/etc/samba
	-$(MAKE) -C $(SAMBA_DIR) clean

samba-dirclean:
	rm -rf $(SAMBA_DIR)
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_SAMBA),y)
TARGETS+=samba
endif
