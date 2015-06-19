#############################################################
#
# netkit-rsh
#
#############################################################

NETKIT_RSH_VERSION:=0.17
NETKIT_RSH_SOURCE:=netkit-rsh_$(NETKIT_RSH_VERSION).orig.tar.gz
NETKIT_RSH_SITE:= $(BR2_DEBIAN_MIRROR)/debian/pool/main/n/netkit-rsh

# uclibc doesn't has rcmd_af() nor ruserok_af(), don't apply patch
# NETKIT_RSH_PATCH = netkit-rsh_0.17-15.diff.gz

NETKIT_RSH_LIBTOOL_PATCH = NO
NETKIT_RSH_INSTALL_STAGING = NO

NETKIT_RSH_DEPENDENCIES = host-fakeroot

$(eval $(call AUTOTARGETS,package,netkit-rsh))

$(NETKIT_RSH_TARGET_CONFIGURE):
	( cd $(NETKIT_RSH_DIR); \
	echo -e \\n\
	CC=$(TARGET_CC)\\n\
	CFLAGS=$(TARGET_CFLAGS)\\n\
	LDFLAGS=$(TARGET_LDFLAGS)\\n\
	USE_PAM=\\n\
	USE_SHADOW=1\\n\
	USE_GLIBC=1\\n\
	LIBTERMCAP=-lncurses\\n\
	LIBSHADOW=\\n\
	LIBS=-lcrypt -lutil\\n\
	INSTALLROOT=$(TARGET_DIR)\\n\
	BINDIR=/usr/bin\\n\
	SBINDIR=/usr/sbin\\n\
	MANDIR=/usr/share/man\\n\
	SUIDMODE=4755\\n\
	BINMODE=755\\n\
	DAEMONMODE=755\\n\
	MANMODE=644\\n\
	> MCONFIG \
	)
	touch $@

$(NETKIT_RSH_TARGET_INSTALL_TARGET):
	$(call MESSAGE,"Installing to target")
	mkdir -p $(TARGET_DIR)/usr/share/man/man{1,8}
	echo '$(MAKE) DESTDIR=$(TARGET_DIR) -C $(NETKIT_RSH_DIR) install' \
		> $(PROJECT_BUILD_DIR)/.fakeroot.netkit-rsh
	chmod +x $(PROJECT_BUILD_DIR)/.fakeroot.netkit-rsh
	fakeroot -- $(PROJECT_BUILD_DIR)/.fakeroot.netkit-rsh
	rm -rf $(TARGET_DIR)/usr/share/man
	touch $@
