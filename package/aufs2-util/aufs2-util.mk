#############################################################
#
# aufs2-util
#
#############################################################

# Current version, use the latest unless there are any known issues.
AUFS-UTIL_VERSION=20090926
# The filename of the package to download.
AUFS-UTIL_SOURCE=aufs2-util-$(AUFS-UTIL_VERSION).tgz
# The site and path to where the source packages are.
AUFS-UTIL_SITE=http://aufs.sourceforge.net
# The directory which the source package is extracted to.
AUFS-UTIL_DIR=$(BUILD_DIR)/aufs2-util-$(AUFS-UTIL_VERSION)
# Which decompression to use, BZCAT or ZCAT.
AUFS-UTIL_CAT:=$(ZCAT)
# Target binary for the package.
AUFS-UTIL_BINARY:=auplink
# Not really needed, but often handy define.
AUFS-UTIL_TARGET_BINARY:=sbin/$(AUFS-UTIL_BINARY)
AUFS-UTIL_SBIN=mount.aufs umount.aufs auplink
AUFS-UTIL_UBIN=auchk aubrsync

# The download rule. Main purpose is to download the source package.
$(DL_DIR)/$(AUFS-UTIL_SOURCE):
	$(call DOWNLOAD,$(AUFS-UTIL_SITE),$(AUFS-UTIL_SOURCE))

# The unpacking rule. Main purpose is to extract the source package, apply any
# patches and update config.guess and config.sub.
$(AUFS-UTIL_DIR)/.unpacked: $(DL_DIR)/$(AUFS-UTIL_SOURCE)
	$(AUFS-UTIL_CAT) $(DL_DIR)/$(AUFS-UTIL_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(AUFS-UTIL_DIR) package/aufs2-util/ aufs2-util-$(AUFS-UTIL_VERSION)-\*.patch\*
	$(CONFIG_UPDATE) $(AUFS-UTIL_DIR)
	touch $@

# The configure rule. Main purpose is to get the package ready for compilation,
# usually by running the configure script with different kinds of options
# specified.
$(AUFS-UTIL_DIR)/.configured: $(AUFS-UTIL_DIR)/.unpacked
	touch $@

$(AUFS-UTIL_DIR)/$(AUFS-UTIL_BINARY): $(AUFS-UTIL_DIR)/.configured
	$(TARGET_CONFIGURE_OPTS) KDIR=$(PROJECT_BUILD_DIR)/linux-2.6.31.1 $(MAKE) -C $(AUFS-UTIL_DIR) auplink mount.aufs
	$(TARGET_CONFIGURE_OPTS) KDIR=$(PROJECT_BUILD_DIR)/linux-2.6.31.1 CC=gcc $(MAKE) -C $(AUFS-UTIL_DIR) etc_default_aufs

# The installing rule. 
$(TARGET_DIR)/$(AUFS-UTIL_TARGET_BINARY): $(AUFS-UTIL_DIR)/$(AUFS-UTIL_BINARY)
	(cd $(AUFS-UTIL_DIR) ;\
	for file in $(AUFS-UTIL_SBIN); do \
		cp -dpf $$file $(TARGET_DIR)/sbin/ ;\
		-$(STRIPCMD) --strip-unneeded $(TARGET_DIR)/sbin/$$file ;\
	done  ;\
	for file in $(AUFS-UTIL_UBIN); do \
		cp -dpf $$file $(TARGET_DIR)/usr/bin/ ;\
	done ;\
	install -m 755 -d $(TARGET_DIR)/etc/default ;\
	cp -dpf etc_default_aufs $(TARGET_DIR)/etc/default/aufs ;\
	)
	
# Main rule which shows which other packages must be installed before the aufs2-util
# package is installed. This to ensure that all depending libraries are
# installed.
aufs2-util:	uclibc $(TARGET_DIR)/$(AUFS-UTIL_TARGET_BINARY)

# Source download rule. Main purpose to download the source package. Since some
# people would like to work offline, it is mandotory to implement a rule which
# downloads everything this package needs.
aufs2-util-source: $(DL_DIR)/$(AUFS-UTIL_SOURCE)

# Clean rule. Main purpose is to clean the build directory, thus forcing a new
# rebuild the next time Buildroot is made.
aufs2-util-clean:
	-$(MAKE) -C $(AUFS-UTIL_DIR) clean

# Directory clean rule. Main purpose is to remove the build directory, forcing
# a new extraction, patching and rebuild the next time Buildroot is made.
aufs2-util-dirclean:
	rm -rf $(AUFS-UTIL_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
# This is how the aufs2-util package is added to the list of rules to build.
ifeq ($(BR2_PACKAGE_AUFS-UTIL),y)
TARGETS+=aufs2-util
endif
