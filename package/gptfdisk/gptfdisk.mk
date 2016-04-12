#############################################################
#
# gptfdisk
#
#############################################################

GPTFDISK_VERSION:=1.0.1
GPTFDISK_SOURCE:=gptfdisk-$(GPTFDISK_VERSION).tar.gz
GPTFDISK_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/gptfdisk/gptfdisk/$(GPTFDISK_VERSION)

GPTFDISK_DIR:=$(BUILD_DIR)/gptfdisk-$(GPTFDISK_VERSION)
GPTFDISK_INSTALL_STAGING = NO
GPTFDISK_LIBTOOL_PATCH = NO

GPTFDISK_CFLAGS = -Os
GPTFDISK_DEPENDENCIES = popt libuuid ncurses
GPTFDISK_MAKE_OPT = sgdisk gdisk cgdisk fixparts

$(eval $(call AUTOTARGETS,package,gptfdisk))

$(GPTFDISK_HOOK_POST_EXTRACT):
	echo -e "#!/bin/bash\necho \"\
CC = \$$CC\\n\
CXX = \$$CXX\\n\
CFLAGS = \$$CFLAGS $(GPTFDISK_CFLAGS)\\n\
CXXFLAGS = \$$CXXFLAGS $(GPTFDISK_CFLAGS)\\n\" >> Makefile" > $(GPTFDISK_DIR)/configure
	sed -i 's/ncursesw/ncurses/' $(GPTFDISK_DIR)/Makefile
	chmod +x $(GPTFDISK_DIR)/configure
	touch $@

$(GPTFDISK_TARGET_INSTALL_TARGET):
ifeq ($(BR2_PACKAGE_GPTFDISK_SGDISK),y)
	cp $(GPTFDISK_DIR)/sgdisk $(TARGET_DIR)/usr/sbin
endif
ifeq ($(BR2_PACKAGE_GPTFDISK_GDISK),y)
	cp $(GPTFDISK_DIR)/gdisk $(TARGET_DIR)/usr/sbin
endif
ifeq ($(BR2_PACKAGE_GPTFDISK_FIXPARTS),y)
	cp $(GPTFDISK_DIR)/fixparts $(TARGET_DIR)/usr/sbin
endif
ifeq ($(BR2_PACKAGE_GPTFDISK_CGDISK),y)
	cp $(GPTFDISK_DIR)/cgdisk $(TARGET_DIR)/usr/sbin
endif
	touch $@
