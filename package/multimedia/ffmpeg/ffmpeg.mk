#############################################################
#
# ffmpef
#
#############################################################
FFMPEG_VERSION = 0.5.1
FFMPEG_SOURCE = ffmpeg-$(FFMPEG_VERSION).tar.bz2
FFMPEG_SITE = http://ffmpeg.org/releases/
FFMPEG_AUTORECONF = NO
FFMPEG_INSTALL_STAGING = YES
FFMPEG_INSTALL_TARGET = YES
FFMPEG_LIBTOOL_PATCH = NO
FFMPEG_DIR:=$(BUILD_DIR)/ffmpeg-$(FFMPEG_VERSION)
FFMPEG_CAT:=$(BZCAT)
FFMPEG_BINARY = ffmpeg
FFMPEG_TARGET_BINARY = usr/bin/$(FFMPEG_BINARY)

$(DL_DIR)/$(FFMPEG_SOURCE):
	$(call DOWNLOAD,$(FFMPEG_SITE),$(FFMPEG_SOURCE))
	
$(FFMPEG_DIR)/.unpacked: $(DL_DIR)/$(FFMPEG_SOURCE)
	$(FFMPEG_CAT) $(DL_DIR)/$(FFMPEG_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(FFMPEG_DIR)/.configured: $(FFMPEG_DIR)/.unpacked
	(cd $(FFMPEG_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		CFLAGS="$(TARGET_CFLAGS) $(FFMPEG_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		./configure \
		--prefix=/usr \
		--enable-cross-compile \
		--cross-prefix=arm-linux-uclibcgnueabi- \
		--host-cc=$(HOSTCC) \
		--cc=$(TARGET_CC) \
		--enable-shared \
		--disable-static \
		--arch=arm \
		--cpu=armv5te \
		--disable-ipv6 \
	)
	touch $@

$(FFMPEG_DIR)/$(FFMPEG_BINARY): $(FFMPEG_DIR)/.configured
	$(MAKE) -C $(FFMPEG_DIR)
	touch -c $@

$(STAGING_DIR)/$(FFMPEG_TARGET_BINARY): $(FFMPEG_DIR)/$(FFMPEG_BINARY)
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(FFMPEG_DIR) install
	touch -c $@

$(TARGET_DIR)/$(FFMPEG_TARGET_BINARY): $(STAGING_DIR)/$(FFMPEG_TARGET_BINARY)
	cp -dpf $(STAGING_DIR)/usr/lib/libavcodec.so* \
	$(STAGING_DIR)/usr/lib/libavformat.so* \
	$(STAGING_DIR)/usr/lib/libavutil.so* $(TARGET_DIR)/usr/lib/
	-$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/libavcodec.so* $(TARGET_DIR)/usr/lib/libavformat.so* $(TARGET_DIR)/usr/lib/libavutil.so*
	cp -dpf $(STAGING_DIR)/usr/bin/ffmpeg $(STAGING_DIR)/usr/bin/ffserver $(TARGET_DIR)/usr/bin
	-$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/bin/ffmpeg $(TARGET_DIR)/usr/bin/ffserver
	touch -c $@

ffmpeg: uclibc $(TARGET_DIR)/$(FFMPEG_TARGET_BINARY)

ffmpeg-source: $(DL_DIR)/$(FFMPEG_SOURCE)

ffmpeg-unpacked: $(FFMPEG_DIR)/.unpacked

ffmpeg-configure: $(FFMPEG_DIR)/.configured

ffmpeg-clean:
	rm -f $(TARGET_DIR)/$(FFMPEG_TARGET_BINARY)
	-$(MAKE) -C $(FFMPEG_DIR) clean

ffmpeg-dirclean:
	rm -rf $(FFMPEG_DIR)
#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_FFMPEG),y)
TARGETS+=ffmpeg
endif
