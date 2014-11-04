#############################################################
#
# pptpd
#
#############################################################

PPTPD_VERSION:=1.3.4
PPTPD_SOURCE:=pptpd-$(PPTPD_VERSION).tar.gz
PPTPD_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/poptop/pptpd/pptpd-$(PPTPD_VERSION)

PPTPD_DEPENDENCIES = uclibc pppd

PPTPD_MAKE_OPT = CC="$(TARGET_CC) $(TARGET_CFLAGS)"

$(eval $(call AUTOTARGETS,package,pptpd))

# hack pppd version
#ver=$(awk '/VERSION/{print $3}' $(PPPD_DIR)/pppd/patchlevel.h)
#sed -i '/VERSION/s/"2.4.3"/'$ver'/' $(PPTPD_DIR)/plugins/patchlevel.h

$(PPTPD_HOOK_POST_EXTRACT):
	$(SED) '/VERSION/s/2.4.3/2.4.5/' $(PPTPD_DIR)/plugins/patchlevel.h
	touch $@

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
