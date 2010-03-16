#############################################################
#
# fuppes
#
#############################################################
FUPPES_VERSION = 660
FUPPES_SOURCE = fuppes-0.$(FUPPES_VERSION).tar.gz
FUPPES_SITE = http://downloads.sourceforge.net/project/fuppes/fuppes/SVN-$(FUPPES_VERSION)
FUPPES_INSTALL_STAGING = NO
FUPPES_INSTALL_TARGET = YES
FUPPES__DEPENDENCIES = uclibc pcre libxml2 sqlite
FUPPES_CONF_ENV += MYSQL_CONFIG=no

$(eval $(call AUTOTARGETS,package,fuppes))
