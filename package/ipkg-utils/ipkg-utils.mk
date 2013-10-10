#############################################################
#
# ipkg-utils for the host
#
#############################################################

IPKG_UTILS_VERSION = 050831
IPKG_UTILS_SOURCE = ipkg-utils-$(IPKG_UTILS_VERSION).tar.gz
# original is down
# IPKG_UTILS_SITE = http://www.handhelds.org/download/packages/ipkg/
IPKG_UTILS_SITE = http://ftp.gwdg.de/linux/handhelds/packages/ipkg-utils

IPKG_UTILS_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS_HOST,package,ipkg-utils))

$(IPKG_UTILS_HOST_CONFIGURE):
	touch $@

$(IPKG_UTILS_HOST_BUILD):
	touch $@

$(IPKG_UTILS_HOST_INSTALL):
	( cd $(IPKG_UTILS_HOST_DIR); \
		sed -i 's|*control|./control|' ipkg.py; \
		sed -i '1s/python/python -W ignore/' ipkg-make-index; \
		sed -i 's/.*Packaged contents.*/#&/' ipkg-build; \
		cp ipkg-build ipkg-make-index ipkg.py $(HOST_DIR)/usr/bin \
	)
	touch $@