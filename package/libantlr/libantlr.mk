#############################################################
#
# libantlr
#
#############################################################

LIBANTLR_VERSION:=3.2
LIBANTLR_SITE = http://www.antlr3.org/download/C/
LIBANTLR_SOURCE = libantlr3c-$(LIBANTLR_VERSION).tar.gz
LIBANTLR_DIR = $(BUILD_DIR)/antlr-$(LIBANTLR_VERSION)
LIBANTLR_LIBTOOL_PATCH = NO
LIBANTLR_INSTALL_STAGING = YES
LIBANTLR_INSTALL_TARGET = YES

LIBANTLRL_CONF_OPT = --disable-static --enable-shared

$(eval $(call AUTOTARGETS,package,libantlr))
