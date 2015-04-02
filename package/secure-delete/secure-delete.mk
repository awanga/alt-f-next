#############################################################
#
# secure-delete
#
#############################################################

SECURE_DELETE_VERSION:=3.1
SECURE_DELETE_SOURCE:=secure-delete_$(SECURE_DELETE_VERSION).orig.tar.gz
SECURE_DELETE_SITE:=$(BR2_DEBIAN_MIRROR)/debian/pool/main/s/secure-delete

SECURE_DELETE_PATCH:=secure-delete_$(SECURE_DELETE_VERSION)-6.diff.gz

SECURE_DELETE_LIBTOOL_PATCH = NO
SECURE_DELETE_INSTALL_STAGING = NO

SECURE_DELETE_MAKE = $(MAKE1)

$(eval $(call AUTOTARGETS,package,secure-delete))

$(SECURE_DELETE_HOOK_POST_CONFIGURE):
	$(SED) 's|CC=.*|CC=$(TARGET_CC)|;/CC=/a CFLAGS=$(TARGET_CFLAGS)' $(SECURE_DELETE_DIR)/Makefile
	touch $@

$(SECURE_DELETE_TARGET_INSTALL_TARGET):
	-mv $(TARGET_DIR)/usr/bin/srm $(TARGET_DIR)/usr/bin/srm-other
	$(MAKE) -C $(SECURE_DELETE_DIR) prefix=$(TARGET_DIR)/usr install
	mv $(TARGET_DIR)/usr/bin/srm $(TARGET_DIR)/usr/bin/srm2
	-mv $(TARGET_DIR)/usr/bin/srm-other $(TARGET_DIR)/usr/bin/srm
	touch $@
