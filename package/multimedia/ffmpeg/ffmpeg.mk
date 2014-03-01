#############################################################
#
# ffmpef
#
#############################################################

FFMPEG_VERSION = 1.2.4
FFMPEG_SOURCE = ffmpeg-$(FFMPEG_VERSION).tar.bz2
FFMPEG_SITE = http://ffmpeg.org/releases/

FFMPEG_AUTORECONF = NO
FFMPEG_LIBTOOL_PATCH = NO

FFMPEG_INSTALL_STAGING = YES
FFMPEG_INSTALL_TARGET = YES

FFMPEG_DIR:=$(BUILD_DIR)/ffmpeg-$(FFMPEG_VERSION)
FFMPEG_CAT:=$(BZCAT)
FFMPEG_BINARY = ffmpeg
FFMPEG_BINARIES = ffmpeg ffserver ffprobe
FFMPEG_TARGET_BINARY = usr/bin/$(FFMPEG_BINARY)
FFMPEG_TARGET_LIBS = usr/lib/libavcodec.so

# don't enable, libmp3lame causes issues
#FFMPEG_CONF_OPT = --enable-libmp3lame --enable-libtheora --enable-libvorbis 

FFMPEG_DEPENDENCIES = uclibc libiconv

$(DL_DIR)/$(FFMPEG_SOURCE):
	$(call DOWNLOAD,$(FFMPEG_SITE),$(FFMPEG_SOURCE))
	
$(FFMPEG_DIR)/.unpacked: $(DL_DIR)/$(FFMPEG_SOURCE)
	$(FFMPEG_CAT) $(DL_DIR)/$(FFMPEG_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(FFMPEG_DIR) package/multimedia/ffmpeg/ ffmpeg-$(FFMPEG_VERSION)\*.patch
	touch $@

$(FFMPEG_DIR)/.configured: $(FFMPEG_DIR)/.unpacked
	(cd $(FFMPEG_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		CFLAGS="$(TARGET_CFLAGS)" \
		LDFLAGS="$(TARGET_LDFLAGS)" \
		./configure \
		--prefix=/usr \
		--enable-cross-compile --cross-prefix=arm-linux-uclibcgnueabi- \
		--host-cc=$(HOSTCC) --cc=$(TARGET_CC) \
		--enable-shared --enable-pic --disable-static --disable-debug \
		--target-os=linux \
		--arch=arm --cpu=armv5te --disable-armv6 --disable-armv6t2 --disable-runtime-cpudetect \
		--disable-hwaccels --disable-vfp --disable-neon \
		--enable-swscale --disable-devices \
		--enable-small --disable-bzlib \
		$(FFMPEG_CONF_OPT) \
	)
	touch $@

#		--disable-programs --disable-bsfs --disable-safe-bitstream-reader \
#		--disable-filters --disable-avfilter --disable-avformat --disable-swresample \
#		--disable-zlib --disable-network

$(FFMPEG_DIR)/$(FFMPEG_BINARY): $(FFMPEG_DIR)/.configured
	$(MAKE) -C $(FFMPEG_DIR)
	touch -c $@

$(STAGING_DIR)/$(FFMPEG_TARGET_BINARY): $(FFMPEG_DIR)/$(FFMPEG_BINARY)
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(FFMPEG_DIR) install
	touch -c $@

$(TARGET_DIR)/$(FFMPEG_TARGET_LIBS): $(STAGING_DIR)/$(FFMPEG_TARGET_BINARY)
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(FFMPEG_DIR) install-progs
ifneq ($(BR2_PACKAGE_FFMPEG_PROGS),y)
	(cd $(TARGET_DIR)/usr/bin; rm -f $(FFMPEG_BINARIES))
endif
	touch -c $@

#$(TARGET_DIR)/$(FFMPEG_TARGET_BINARY): $(STAGING_DIR)/$(FFMPEG_TARGET_BINARY)
#	mkdir -p $(STAGING_DIR)/usr/include/ffmpeg
#	for i in libavcodec libavformat libavdevice libavutil libswscale libavfilter libswresample; do \
#		cp -dpf $(STAGING_DIR)/usr/lib/$$i.so* $(TARGET_DIR)/usr/lib/; \
#		$(STRIPCMD) $(STRIP_STRIP_UNNEEDED) $(TARGET_DIR)/usr/lib/$$i.so*; \
#		cp $(STAGING_DIR)/usr/include/$$i/* $(STAGING_DIR)/usr/include/ffmpeg; \
#	done
#	(cd $(STAGING_DIR)/usr/bin; cp -dpf $(FFMPEG_BINARIES) $(TARGET_DIR)/usr/bin)
#	(cd $(TARGET_DIR)/usr/bin; $(STRIPCMD) $(FFMPEG_BINARIES) )
#	touch -c $@

ffmpeg: $(FFMPEG_DEPENDENCIES) $(TARGET_DIR)/$(FFMPEG_TARGET_LIBS)

ffmpeg-source: $(DL_DIR)/$(FFMPEG_SOURCE)

ffmpeg-unpacked: $(FFMPEG_DIR)/.unpacked

ffmpeg-configure: $(FFMPEG_DIR)/.configured

ffmpeg-clean:
	rm -f $(TARGET_DIR)/$(FFMPEG_TARGET_BINARY) \
		$(TARGET_DIR)/$(FFMPEG_TARGET_BINARY2) \
		$(TARGET_DIR)/usr/lib/libavcodec.so* \
		$(TARGET_DIR)/usr/lib/libavformat.so* \
		$(TARGET_DIR)/usr/lib/libavdevice.so* \
		$(TARGET_DIR)/usr/lib/libavutil.so* \
		$(TARGET_DIR)/usr/lib/libavfilter.so*
	-$(MAKE) -C $(FFMPEG_DIR) clean

ffmpeg-uninstall:
	$(MAKE) DESTDIR=$(STAGING_DIR) -C $(FFMPEG_DIR) uninstall
	$(MAKE) DESTDIR=$(TARGET_DIR) -C $(FFMPEG_DIR) uninstall
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
