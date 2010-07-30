#############################################################
#
# foomatic-filters
#
#############################################################
FOOMATIC_FILTERS_VERSION = 4.0.4
FOOMATIC_FILTERS_SOURCE = foomatic-filters-$(FOOMATIC_FILTERS_VERSION).tar.gz
FOOMATIC_FILTERS_SITE = http://www.openprinting.org/download/foomatic/
FOOMATIC_FILTERS_INSTALL_STAGING = YES
FOOMATIC_FILTERS_INSTALL_TARGET = YES
FOOMATIC_FILTERS_DEPENDENCIES = uclibc cups a2ps gs
FOOMATIC_FILTERS_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install-main install-cups

$(eval $(call AUTOTARGETS,package,foomatic-filters))
