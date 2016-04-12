#############################################################
#
# ipkg-utils for the host
#
#############################################################

IPKG_UTILS_VERSION = 050831
IPKG_UTILS_SOURCE = ipkg-utils-$(IPKG_UTILS_VERSION).tar.gz
IPKG_UTILS_SITE = ftp://ftp.gwdg.de/pub/linux/handhelds/packages/ipkg-utils

IPKG_UTILS_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS_HOST,package,ipkg-utils))

$(IPKG_UTILS_HOST_CONFIGURE):
	touch $@

$(IPKG_UTILS_HOST_BUILD):
	touch $@

$(IPKG_UTILS_HOST_INSTALL):
	( cd $(IPKG_UTILS_HOST_DIR); \
		$(SED) 's|*control|./control|' ipkg.py; \
		$(SED) 's/.*Packaged contents.*/#&/' \
			-e 's/tar /tar --format=gnu /' ipkg-build; \
		cp ipkg-build ipkg-make-index ipkg.py $(HOST_DIR)/usr/bin \
	)
	touch $@
