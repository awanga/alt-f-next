#############################################################
#
# libffi
#
############################################################

LIBFFI_VERSION = 3.2.1
LIBFFI_SOURCE = libffi-$(LIBFFI_VERSION).tar.gz
LIBFFI_SITE = ftp://sourceware.org/pub

LIBFFI_LIBTOOL_PATCH = NO
LIBFFI_INSTALL_STAGING = YES
LIBFFI_INSTALL_TARGET = YES
LIBFFI_CONF_OPT = --disable-static
LIBFFI_DEPENDENCIES = uclibc 

$(eval $(call AUTOTARGETS,package,libffi))
