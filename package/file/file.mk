#############################################################
#
# file
#
#############################################################
#FILE_VERSION:=4.26
FILE_VERSION:=5.04
FILE_SOURCE:=file-$(FILE_VERSION).tar.gz
FILE_SITE:=ftp://ftp.astron.com/pub/file/
#FILE_SOURCE_DIR:=$(BUILD_DIR)/file-$(FILE_VERSION)
FILE_DIR:=$(BUILD_DIR)/file-$(FILE_VERSION)
FILE_HOST:=$(BUILD_DIR)/file-$(FILE_VERSION)-host
FILE_CAT:=$(ZCAT)
FILE_BINARY:=src/file
FILE_TARGET_BINARY:=usr/bin/file

#############################################################
#
# build file for use on the host system
#
#############################################################

$(FILE_HOST)/.unpacked: $(DL_DIR)/$(FILE_SOURCE)
	mkdir -p $(FILE_HOST)
	$(FILE_CAT) $(DL_DIR)/$(FILE_SOURCE) | tar $(TAR_STRIP_COMPONENTS)=1 -C $(FILE_HOST) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(FILE_HOST) package/file/ file\*.patch
	$(CONFIG_UPDATE) $(FILE_HOST)
	touch $@

$(FILE_HOST)/.configured: $(FILE_HOST)/.unpacked
	#$(MAKE) -C $(FILE_DIR) distclean
	#(cd $(FILE_DIR) && rm config.guess config.sub)
	mkdir -p $(FILE_HOST)
	(cd $(FILE_HOST); rm -rf config.cache; \
		CC="$(HOSTCC)" \
		$(FILE_HOST)/configure \
		--prefix=$(STAGING_DIR) \
	)
	touch $@

$(STAGING_DIR)/$(FILE_TARGET_BINARY): $(FILE_HOST)/.configured
	$(MAKE) -C $(FILE_HOST) install
	ln -sf $(STAGING_DIR)/bin/file $(TOOL_BUILD_DIR)/bin/file

#host-file: $(TOOL_BUILD_DIR)/bin/file
#
#host-file-clean:
#	-$(MAKE) -C $(FILE_DIR1) clean
#
#host-file-dirclean:
#	rm -rf $(FILE_DIR1)

#############################################################
#
# build file for use on the target system
#
#############################################################

$(DL_DIR)/$(FILE_SOURCE):
	 $(call DOWNLOAD,$(FILE_SITE),$(FILE_SOURCE))

$(FILE_DIR)/.unpacked: $(DL_DIR)/$(FILE_SOURCE)
	$(FILE_CAT) $(DL_DIR)/$(FILE_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(FILE_DIR) package/file/ file\*.patch
	$(CONFIG_UPDATE) $(FILE_DIR)
	touch $@

$(FILE_DIR)/.configured: $(FILE_DIR)/.unpacked
	(cd $(FILE_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(FILE_DIR)/configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--bindir=/usr/bin \
		--sbindir=/usr/sbin \
		--libdir=/usr/lib \
		--libexecdir=/usr/lib \
		--sysconfdir=/etc \
		--datadir=/usr/share/ \
		--localstatedir=/var \
		--mandir=/usr/share/man \
		--infodir=/usr/share/info \
		$(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
		--disable-static \
		--disable-fsect-man5 \
	)
	touch $@

$(FILE_DIR)/$(FILE_BINARY): $(FILE_DIR)/.configured
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(FILE_DIR)

$(TARGET_DIR)/$(FILE_TARGET_BINARY): $(FILE_DIR)/$(FILE_BINARY)
	$(MAKE) $(TARGET_CONFIGURE_OPTS) DESTDIR=$(TARGET_DIR) -C $(FILE_DIR) install


file-host: $(STAGING_DIR)/$(FILE_TARGET_BINARY)

file-target: $(TARGET_DIR)/$(FILE_TARGET_BINARY)

file: zlib uclibc file-host file-target

#$(STAGING_DIR)/$(FILE_TARGET_BINARY) 

file-source: $(DL_DIR)/$(FILE_SOURCE)

file-unpacked: $(FILE_DIR)/.unpacked

file-configure: $(FILE_DIR)/.configured

file-build: $(FILE_DIR)/$(FILE_BINARY)

file-install: $(TARGET_DIR)/$(FILE_TARGET_BINARY)

file-clean:
	-$(MAKE) DESTDIR=$(TARGET_DIR) CC=$(TARGET_CC) -C $(FILE_DIR) uninstall
	-$(MAKE) -C $(FILE_DIR) clean

file-dirclean:
	rm -rf $(FILE_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_FILE),y)
TARGETS+=file
endif
