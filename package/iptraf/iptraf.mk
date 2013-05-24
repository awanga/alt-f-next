#############################################################
#
# iptraf
#
#############################################################

IPTRAF_VERSION:=3.0.0
IPTRAF_SOURCE:=iptraf-$(IPTRAF_VERSION).tar.gz
IPTRAF_SITE:=ftp://iptraf.seul.org/pub/iptraf
IPTRAF_DIR:=$(BUILD_DIR)/iptraf-$(IPTRAF_VERSION)
IPTRAF_AUTORECONF:=NO
IPTRAF_INSTALL_STAGING:=NO
IPTRAF_INSTALL_TARGET:=YES
IPTRAF_TARGET_BINARY:=/usr/sbin/iptraf
IPTRAF_TARGET_BINARY2:=/usr/sbin/rvnamed
IPTRAF_BINARY:=src/iptraf
IPTRAF_BINARY2:=src/rvnamed

$(DL_DIR)/$(IPTRAF_SOURCE):
	 $(call DOWNLOAD,$(IPTRAF_SITE),$(IPTRAF_SOURCE))

iptraf-source: $(DL_DIR)/$(IPTRAF_SOURCE)

$(IPTRAF_DIR)/.unpacked: $(DL_DIR)/$(IPTRAF_SOURCE)
	$(ZCAT) $(DL_DIR)/$(IPTRAF_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(IPTRAF_DIR) package/iptraf/ iptraf\*.patch
	sed -i -e 's/gcc.*-O2/$$(CC) $$(CFLAGS)/' \
		-e 's/ar /$$(AR) /' \
		-e 's/ranlib /$$(RANLIB) /' \
		$(IPTRAF_DIR)/support/Makefile
	touch $(IPTRAF_DIR)/.unpacked

$(IPTRAF_DIR)/$(IPTRAF_BINARY): $(IPTRAF_DIR)/.unpacked
	$(MAKE) CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" \
		INCLUDEDIR="-I/$(STAGING_DIR)/usr/include -I../support" \
		AR="$(TARGET_AR)" \
		RANLIB="$(TARGET_RANLIB)" \
		-C $(IPTRAF_DIR)/src all
	$(STRIPCMD) $(IPTRAF_DIR)/$(IPTRAF_BINARY) $(IPTRAF_DIR)/$(IPTRAF_BINARY2)

$(TARGET_DIR)/$(IPTRAF_TARGET_BINARY): $(IPTRAF_DIR)/$(IPTRAF_BINARY)
	$(INSTALL) -m 0755 -D $(IPTRAF_DIR)/$(IPTRAF_BINARY) $(TARGET_DIR)/$(IPTRAF_TARGET_BINARY)
	$(INSTALL) -m 0755 -D $(IPTRAF_DIR)/$(IPTRAF_BINARY2) $(TARGET_DIR)/$(IPTRAF_TARGET_BINARY2)

iptraf: uclibc ncurses $(TARGET_DIR)/$(IPTRAF_TARGET_BINARY)

iptraf-build: $(IPTRAF_DIR)/$(IPTRAF_BINARY)

iptraf-clean:
	rm -f $(TARGET_DIR)/$(IPTRAF_TARGET_BINARY)
	-$(MAKE) -C $(IPTRAF_DIR)/src clean
	-$(MAKE) -C $(IPTRAF_DIR)/support clean

iptraf-dirclean:
	rm -rf $(IPTRAF_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_IPTRAF),y)
TARGETS+=iptraf
endif


