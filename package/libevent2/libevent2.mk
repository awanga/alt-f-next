#############################################################
#
# libevent2
#
#############################################################

# transmission 2.22 needs libevent 2.0.10, but forked-daapd
# does not work with it, needs libevent 1.4.13.
# So, until forked works with libevent 2.0.x, a new package
# named libevent 2 (this one) is created.
# As the header and libraries of libevent1 and libevent2 can't be mixed,
# libevent2 installs in the staging dir in directory libevent2, and
# transmission.mk is directed to search it there. Other apps will see and
# use libevent1.

LIBEVENT2_VERSION:=2.0.10
LIBEVENT2_SOURCE:=libevent-$(LIBEVENT2_VERSION)-stable.tar.gz
LIBEVENT2_SITE:=http://monkey.org/~provos/
LIBEVENT2_DIR:=$(BUILD_DIR)/libevent-$(LIBEVENT2_VERSION)-stable
LIBEVENT2_CAT:=$(ZCAT)
LIBEVENT2_BINARY:=libevent.la
LIBEVENT2_TARGET_BINARY:=usr/lib/libevent-2.0.so.5
LIBEVENT2_STAGING_BINARY:=libevent2/lib/libevent-2.0.so.5

$(DL_DIR)/$(LIBEVENT2_SOURCE):
	$(call DOWNLOAD,$(LIBEVENT2_SITE),$(LIBEVENT2_SOURCE))

libevent2-source: $(DL_DIR)/$(LIBEVENT2_SOURCE)

libevent2-unpacked: $(LIBEVENT2_DIR)/.unpacked

$(LIBEVENT2_DIR)/.unpacked: $(DL_DIR)/$(LIBEVENT2_SOURCE)
	$(LIBEVENT2_CAT) $(DL_DIR)/$(LIBEVENT2_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(LIBEVENT2_DIR) package/libevent2/ \*.patch
	touch $@

$(LIBEVENT2_DIR)/.configured: $(LIBEVENT2_DIR)/.unpacked
	(cd $(LIBEVENT2_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/libevent2 \
		--libdir=/libevent2/lib \
		--mandir=/usr/share/man \
		--disable-static \
		--with-gnu-ld \
		--disable-openssl --disable-thread-support \
	)
	touch $@

$(LIBEVENT2_DIR)/$(LIBEVENT2_BINARY): $(LIBEVENT2_DIR)/.configured
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(LIBEVENT2_DIR)

$(STAGING_DIR)/$(LIBEVENT2_STAGING_BINARY): $(LIBEVENT2_DIR)/$(LIBEVENT2_BINARY)
	$(MAKE) -C $(LIBEVENT2_DIR) DESTDIR=$(STAGING_DIR) install
	( cd $(STAGING_DIR)/libevent2/lib/; mv libevent.so libevent2.so; mv libevent_core.so libevent2_core.so; mv libevent_extra.so libevent2_extra.so )

$(TARGET_DIR)/$(LIBEVENT2_TARGET_BINARY): $(STAGING_DIR)/$(LIBEVENT2_STAGING_BINARY)
	cp -a $(STAGING_DIR)/libevent2/lib/libevent*.so* $(TARGET_DIR)/usr/lib/
	#$(MAKE) -C $(LIBEVENT2_DIR) DESTDIR=$(TARGET_DIR) install
	#rm -rf $(addprefix $(TARGET_DIR)/usr/,lib/libevent*.la \
					     include/ev*)

ifneq ($(BR2_HAVE_MANPAGES),y)
	rm -fr $(TARGET_DIR)/usr/share/man
endif

libevent2-configure: $(LIBEVENT2_DIR)/.configured

libevent2-build: $(LIBEVENT2_DIR)/$(LIBEVENT2_BINARY)

libevent2-staging: $(STAGING_DIR)/libevent2/lib/$(LIBEVENT2_STAGING_BINARY)

libevent2: uclibc $(TARGET_DIR)/$(LIBEVENT2_TARGET_BINARY)

libevent2-clean:
	rm -f $(TARGET_DIR)/$(LIBEVENT2_TARGET_BINARY)*
	-$(MAKE) -C $(LIBEVENT2_DIR) clean

libevent2-dirclean:
	rm -rf $(LIBEVENT2_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_LIBEVENT2),y)
TARGETS+=libevent2
endif
