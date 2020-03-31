#############################################################
#
# UNRAR
#
#############################################################
UNRAR_VERSION = 5.5.8
UNRAR_SOURCE = unrarsrc-$(UNRAR_VERSION).tar.gz
UNRAR_SITE = http://www.rarlab.com/rar

UNRAR_DIR:=$(BUILD_DIR)/unrar-$(UNRAR_VERSION)
UNRAR_AUTORECONF:=NO
UNRAR_INSTALL_STAGING:=NO
UNRAR_INSTALL_TARGET:=YES
UNRAR_BINARY:=unrar
UNRAR_TARGET_BINARY:=usr/bin/unrar

$(DL_DIR)/$(UNRAR_SOURCE):
	$(call DOWNLOAD,$(UNRAR_SITE),$(UNRAR_SOURCE))
    
$(UNRAR_DIR)/.source: $(DL_DIR)/$(UNRAR_SOURCE)
	$(ZCAT) $(DL_DIR)/$(UNRAR_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	mv $(BUILD_DIR)/unrar $(UNRAR_DIR)
	toolchain/patch-kernel.sh $(UNRAR_DIR) package/unrar/ \*-$(UNRAR_VERSION).patch
	touch $@

$(UNRAR_DIR)/$(UNRAR_BINARY): $(UNRAR_DIR)/.source
	$(MAKE) CXX=$(TARGET_CXX) CPPFLAGS="$(TARGET_CFLAGS)" STRIP=$(TARGET_STRIP) -C $(UNRAR_DIR)

$(TARGET_DIR)/$(UNRAR_TARGET_BINARY): $(UNRAR_DIR)/$(UNRAR_BINARY)
	$(MAKE) DESTDIR=$(TARGET_DIR)/usr -C $(UNRAR_DIR) install
	
unrar: uclibc $(TARGET_DIR)/$(UNRAR_TARGET_BINARY)

unrar-build: $(UNRAR_DIR)/$(UNRAR_BINARY)

unrar-source: $(DL_DIR)/$(UNRAR_SOURCE)

unrar-clean:
	$(MAKE) prefix=$(TARGET_DIR)/usr -C $(UNRAR_DIR) uninstall
	-$(MAKE) -C $(UNRAR_DIR) clean

unrar-dirclean:
	rm -rf $(UNRAR_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_UNRAR),y)
TARGETS+=unrar
endif
