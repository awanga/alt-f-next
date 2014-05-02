#############################################################
#
# msmtp
#
#############################################################

MSMTP_VERSION = 1.4.31
MSMTP_SOURCE = msmtp-$(MSMTP_VERSION).tar.bz2
MSMTP_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/msmtp/msmtp/$(MSMTP_VERSION)

MSMTP_INSTALL_STAGING = NO
MSMTP_INSTALL_TARGET = YES
MSMTP_BINARY:=src/msmtp
MSMTP_TARGET_BINARY:=usr/bin/msmtp

MSMTP_CONF_OPT = --program-prefix="" --with-ssl=openssl --without-gnome-keyring --without-libidn
MSMTP_CONF_ENV = PKG_CONFIG=/usr/bin/pkg-config

MSMTP_DEPENDENCIES = uclibc openssl

$(eval $(call AUTOTARGETS,package,msmtp))
