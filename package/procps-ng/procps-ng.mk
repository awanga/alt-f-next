#############################################################
#
# procps-ng
#
#############################################################

# package has a broken --prefix/DESTDIR handling
#
# install in /usr/local, to not conflict with busybox binaries
# pkg install script should edit /etc/profile to adjust PATH

PROCPS_NG_VERSION:=3.3.10
PROCPS_NG_SOURCE:=procps-ng-$(PROCPS_NG_VERSION).tar.xz
PROCPS_NG_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/procps-ng/Production

PROCPS_NG_AUTORECONF = NO
PROCPS_NG_LIBTOOL_PATCH = NO

PROCPS_NG_CONF_OPT = \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/ \
		--exec-prefix=/ \
		--libdir=/lib \
		--libexecdir=/lib \
		--sysconfdir=/etc \
		$(DISABLE_DOCUMENTATION) \
		$(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
		$(DISABLE_IPV6) \
		$(QUIET)

$(eval $(call AUTOTARGETS,package,procps-ng))

PROCPS_NG_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR)/usr/local install-strip

$(PROCPS_NG_HOOK_POST_INSTALL):
	( cd $(TARGET_DIR) ; \
		mv ./usr/local/lib/lib*.so* ./usr/lib/; \
		rm -rf ./usr/local/share \
			./usr/local/include \
			./usr/local/lib; \
		for i in top uptime free kill ps pidof watch; do \
			ln -sf /usr/local/bin/$$i ./usr/bin/p$$i; \
		done \
	)
	touch $@