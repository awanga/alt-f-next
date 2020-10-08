################################################################################
#
# libantlr3
#
################################################################################

LIBANTLR3_VERSION = 3.4
LIBANTLR3_SITE = https://www.antlr3.org/download/C
LIBANTLR3_SOURCE = libantlr3c-$(LIBANTLR3_VERSION).tar.gz
LIBANTLR3_INSTALL_STAGING = YES
LIBANTLR3_LICENSE = BSD
LIBANTLR3_LICENSE_FILES = COPYING

$(eval $(autotools-package))
