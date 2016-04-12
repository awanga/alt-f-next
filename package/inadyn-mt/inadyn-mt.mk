#############################################################
#
# inadyn-mt
#
#############################################################

INADYN_MT_VERSION = 02.24.49
INADYN_MT_SOURCE = inadyn-mt.v.$(INADYN_MT_VERSION).tar.gz
INADYN_MT_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/inadyn-mt/inadyn-mt/inadyn-mt.v.$(INADYN_MT_VERSION)

INADYN_MT_AUTORECONF = NO
INADYN_MT_INSTALL_STAGING = NO
INADYN_MT_INSTALL_TARGET = YES

INADYN_MT_DEPENDENCIES = uclibc
INADYN_MT_CONF_OPT = --program-prefix="" --disable-sound -enable-threads

$(eval $(call AUTOTARGETS,package,inadyn-mt))

$(INADYN_MT_HOOK_POST_EXTRACT):
	sed -i -e 's|$$(INSTALL_PREFIX)|$$(DESTDIR)$$(INSTALL_PREFIX)|' \
		-e 's|mkdir|$$(MKDIR_P)|' \
		$(INADYN_MT_DIR)/Makefile.in
	sed -i -e 's|^inadyn_mt_CFLAGS =.*|inadyn_mt_CFLAGS = $$(CFLAGS) $$(ARCH_SPECIFIC_CFLAGS)|' \
		-e 's|^inadyn_mt_LDFLAGS =.*|inadyn_mt_LDFLAGS = $$(ARCH_SPECIFIC_LDFLAGS)|' \
		$(INADYN_MT_DIR)/src/Makefile.in
	touch $@

$(INADYN_MT_HOOK_POST_INSTALL):
	$(RM) -r $(TARGET_DIR)/usr/inadyn-mt
	touch $@
