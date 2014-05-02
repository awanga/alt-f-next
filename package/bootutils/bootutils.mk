#############################################################
#
# bootutils
#
#############################################################
BOOTUTILS_VERSION = 0.0.9
BOOTUTILS_SITE = $(BR2_SOURCEFORGE_MIRROR)/sourceforge/bootutils

BOOTUTILS_CONF_ENV = ac_cv_func_malloc_0_nonnull=yes

BOOTUTILS_CONF_OPT = --prefix=/ --exec-prefix=/

BOOTUTILS_INSTALL_TARGET_OPT=DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,bootutils))
