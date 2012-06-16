#############################################################
#
# nzbget
#
#############################################################

NZBGET_VERSION = 0.8.0
NZBGET_SOURCE = nzbget-$(NZBGET_VERSION).tar.gz
NZBGET_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/nzbget
NZBGET_AUTORECONF = NO
NZBGET_INSTALL_STAGING = NO
NZBGET_INSTALL_TARGET = YES
NZBGET_LIBTOOL_PATCH = NO
NZBGET_DEPENDENCIES = uclibc libpar2 libxml2 openssl ncurses

NZBGET_CONF_ENV = LIBPREF=$(STAGING_DIR)
NZBGET_CONF_OPT = --program-prefix="" 

#--with-libsigc-includes=" " \

$(eval $(call AUTOTARGETS,package,nzbget))


