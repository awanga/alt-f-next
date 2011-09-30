#############################################################
#
# inadyn
#
#############################################################
INADYN_VERSION:=1.96.2
INADYN_SOURCE:=inadyn.v$(INADYN_VERSION).zip
INADYN_SITE:=http://www.inatech.eu/inadyn
INADYN_DIR:=$(BUILD_DIR)/inadyn-$(INADYN_VERSION)
INADYN_AUTORECONF:=NO
INADYN_INSTALL_STAGING:=NO
INADYN_INSTALL_TARGET:=YES
INADYN_CAT:=$(BZCAT)
INADYN_BINARY:=inadyn
INADYN_TARGET_BINARY:=usr/bin/inadyn

$(DL_DIR)/$(INADYN_SOURCE):
	$(call DOWNLOAD,$(INADYN_SITE),$(INADYN_SOURCE))
    
$(INADYN_DIR)/.source: $(DL_DIR)/$(INADYN_SOURCE)
	unzip $(DL_DIR)/$(INADYN_SOURCE) -d $(BUILD_DIR)
	mv $(BUILD_DIR)/inadyn $(INADYN_DIR)
	patch -p0 -d $(INADYN_DIR) < package/inadyn/inadyn-1.96.2.patch
	touch $@

$(INADYN_DIR)/$(INADYN_BINARY): $(INADYN_DIR)/.source
	$(MAKE) CC=$(TARGET_CC) CFLAGS="$(TARGET_CFLAGS)" -C $(INADYN_DIR)

$(TARGET_DIR)/$(INADYN_TARGET_BINARY): $(INADYN_DIR)/$(INADYN_BINARY)
	$(MAKE) DESTDIR=$(TARGET_DIR)  STRIP=$(TARGET_STRIP) -C $(INADYN_DIR) install
	
inadyn: uclibc $(TARGET_DIR)/$(INADYN_TARGET_BINARY)

inadyn-source: $(DL_DIR)/$(INADYN_SOURCE)

inadyn-clean:
	$(MAKE) prefix=$(TARGET_DIR)/usr -C $(INADYN_DIR) uninstall
	-$(MAKE) -C $(INADYN_DIR) clean

inadyn-dirclean:
	rm -rf $(INADYN_DIR)
    
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_INADYN),y)
TARGETS+=inadyn
endif
