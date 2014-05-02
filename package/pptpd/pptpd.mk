#############################################################
#
# pptpd
#
#############################################################

PPTPD_VERSION:=1.3.4
PPTPD_SOURCE:=pptpd-$(PPTPD_VERSION).tar.gz
PPTPD_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/poptop/pptpd/pptpd-$(PPTPD_VERSION)

PPTPD_DEPENDENCIES = uclibc pppd

$(eval $(call AUTOTARGETS,package,pptpd))

$(PPTPD_TARGET_INSTALL_TARGET):
	$(MAKE) DESTDIR=$(TARGET_DIR) \
	LIBDIR=$(TARGET_DIR)/usr/lib/pptpd \
	INSTALL=/usr/bin/install \
	-C $(PPTPD_DIR) install
	( cd $(PPTPD_DIR)/samples; \
	cp pptpd.conf $(TARGET_DIR)/etc; \
	cp options.pptpd $(TARGET_DIR)/etc/ppp; \
	cat chap-secrets >> $(TARGET_DIR)/etc/ppp/chap-secrets \
	)
	touch $@
