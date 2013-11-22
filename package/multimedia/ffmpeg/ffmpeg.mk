#############################################################
#
# ffmpef
#
#############################################################

FFMPEG_VERSION = 0.6.3
FFMPEG_SOURCE = ffmpeg-$(FFMPEG_VERSION).tar.bz2
FFMPEG_SITE = http://ffmpeg.org/releases/
FFMPEG_AUTORECONF = NO
FFMPEG_INSTALL_STAGING = YES
FFMPEG_INSTALL_TARGET = YES
FFMPEG_LIBTOOL_PATCH = NO
FFMPEG_DIR:=$(BUILD_DIR)/ffmpeg-$(FFMPEG_VERSION)
FFMPEG_CAT:=$(BZCAT)
FFMPEG_BINARY = ffmpeg
FFMPEG_BINARIES = ffmpeg ffserver ffprobe
FFMPEG_TARGET_BINARY = usr/bin/$(FFMPEG_BINARY)

FFMPEG_CONF_OPT = --enable-libmp3lame
# --enable-libtheora --enable-libvorbis 

FFMPEG_DEPENDENCIES = uclibc bzip2 lame

$(DL_DIR)/$(FFMPEG_SOURCE):
	$(call DOWNLOAD,$(FFMPEG_SITE),$(FFMPEG_SOURCE))
	
$(FFMPEG_DIR)/.unpacked: $(DL_DIR)/$(FFMPEG_SOURCE)
	$(FFMPEG_CAT) $(DL_DIR)/$(FFMPEG_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(FFMPEG_DIR) package/multimedia/ffmpeg/ \*.patch
	touch $@

$(FFMPEG_DIR)/.configured: $(FFMPEG_DIR)/.unpacked
	(cd $(FFMPEG_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		CFLAGS="$(TARGET_CFLAGS) $(FFMPEG_CFLAGS) -fpic" \
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
		--target-os=linux \
		$(FFMPEG_CONF_OPT) \
		--disable-devices \
		--disable-debug \
		--disable-stripping \
		--enable-swscale \
	)
	touch $@

$(FFMPEG_DIR)/$(FFMPEG_BINARY): $(FFMPEG_DIR)/.configured
	$(MAKE) -C $(FFMPEG_DIR)
	touch -c $@

$(STAGING_DIR)/$(FFMPEG_TARGET_BINARY): $(FFMPEG_DIR)/$(FFMPEG_BINARY)
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(FFMPEG_DIR) install
	touch -c $@

$(TARGET_DIR)/$(FFMPEG_TARGET_BINARY): $(STAGING_DIR)/$(FFMPEG_TARGET_BINARY)
	mkdir -p $(STAGING_DIR)/usr/include/ffmpeg
	for i in libavcodec libavformat libavdevice libavutil libswscale; do \
		cp -dpf $(STAGING_DIR)/usr/lib/$$i.so* $(TARGET_DIR)/usr/lib/; \
		$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/$$i.so*; \
		cp $(STAGING_DIR)/usr/include/$$i/* $(STAGING_DIR)/usr/include/ffmpeg; \
	done
	(cd $(STAGING_DIR)/usr/bin; cp -dpf $(FFMPEG_BINARIES) $(TARGET_DIR)/usr/bin)
	(cd $(TARGET_DIR)/usr/bin; $(STRIPCMD) $(FFMPEG_BINARIES) )
	touch -c $@

ffmpeg: $(FFMPEG_DEPENDENCIES) $(TARGET_DIR)/$(FFMPEG_TARGET_BINARY)

ffmpeg-source: $(DL_DIR)/$(FFMPEG_SOURCE)

ffmpeg-unpacked: $(FFMPEG_DIR)/.unpacked

ffmpeg-configure: $(FFMPEG_DIR)/.configured

ffmpeg-clean:
	rm -f $(TARGET_DIR)/$(FFMPEG_TARGET_BINARY) \
		$(TARGET_DIR)/$(FFMPEG_TARGET_BINARY2) \
		$(TARGET_DIR)/usr/lib/libavcodec.so* \
		$(TARGET_DIR)/usr/lib/libavformat.so* \
		$(TARGET_DIR)/usr/lib/libavdevice.so* \
		$(TARGET_DIR)/usr/lib/libavutil.so*
	-$(MAKE) -C $(FFMPEG_DIR) clean

ffmpeg-uninstall:
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(FFMPEG_DIR) uninstall
	touch -c $@	

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
