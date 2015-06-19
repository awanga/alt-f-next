#############################################################
#
# libantlr
#
#############################################################

LIBANTLR_VERSION:=3.4
LIBANTLR_SITE = http://www.antlr3.org/download/C/
LIBANTLR_JAR_SITE = http://www.antlr3.org/download/
LIBANTLR_SOURCE = libantlr3c-$(LIBANTLR_VERSION).tar.gz

LIBANTLR_DIR = $(BUILD_DIR)/antlr-$(LIBANTLR_VERSION)
LIBANTLR_LIBTOOL_PATCH = NO
LIBANTLR_INSTALL_STAGING = YES
LIBANTLR_INSTALL_TARGET = YES

LIBANTLR_DEPENDENCIES = libantlr-host

LIBANTLRL_CONF_OPT = --disable-static --enable-shared

$(eval $(call AUTOTARGETS,package,libantlr))
$(eval $(call AUTOTARGETS_HOST,package,libantlr))

$(LIBANTLR_HOST_HOOK_POST_BUILD):
	$(call DOWNLOAD,$(LIBANTLR_JAR_SITE),antlr-$(LIBANTLR_VERSION)-complete.jar)
	mkdir -p $(HOST_DIR)/usr/share/java/
	cp $(DL_DIR)/antlr-$(LIBANTLR_VERSION)-complete.jar $(HOST_DIR)/usr/share/java/
	echo -e '#!/bin/sh \n\
	export CLASSPATH \n\
	CLASSPATH=$$CLASSPATH:$(HOST_DIR)/usr/share/java/antlr-3.4-complete.jar:$(HOST_DIR)/usr/share/java \n\
	/usr/bin/java org.antlr.Tool $$@' > $(HOST_DIR)/usr/bin/antlr3
	chmod +x $(HOST_DIR)/usr/bin/antlr3
	touch $@