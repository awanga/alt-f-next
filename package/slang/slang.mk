#############################################################
#
# slang
#
############################################################

SLANG_VERSION:=2.2.4
SLANG_SOURCE=slang-$(SLANG_VERSION).tar.bz2
SLANG_SITE:= http://www.jedsoft.org/releases/slang/old

SLANG_INSTALL_STAGING = YES
SLANG_INSTALL_TARGET = YES
SLANG_MAKE = $(MAKE1)

# Absolute path hell, sigh...
ifeq ($(BR2_PACKAGE_LIBPNG),y)
SLANG_CONF_OPT += --with-png=$(STAGING_DIR)/usr
SLANG_DEPENDENCIES += libpng
else
SLANG_CONF_OPT += --with-png=no
endif

ifeq ($(BR2_PACKAGE_PCRE),y)
SLANG_CONF_OPT += --with-pcre=$(STAGING_DIR)/usr
SLANG_DEPENDENCIES += pcre
else
SLANG_CONF_OPT += --with-pcre=no
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
SLANG_CONF_OPT += --with-z=$(STAGING_DIR)/usr
SLANG_DEPENDENCIES += zlib
else
SLANG_CONF_OPT += --with-z=no
endif

ifeq ($(BR2_PACKAGE_NCURSES),y)
SLANG_DEPENDENCIES += ncurses
else
SLANG_CONF_OPT += ac_cv_path_nc5config=no
endif

ifeq ($(BR2_PACKAGE_READLINE),y)
SLANG_CONF_OPT += --with-readline=gnu
SLANG_DEPENDENCIES += readline
endif

ifeq ($(BR2_STATIC_LIBS),y)
SLANG_MAKE_OPT = static
SLANG_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) install-static
SLANG_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install-static
else
SLANG_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) install
SLANG_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
endif

$(eval $(call AUTOTARGETS,package,slang))

$(SLANG_HOOK_POST_EXTRACT):
	$(SED) '/^TERMCAP=/s:=.*:=:' $(@D)/configure
	touch $@
