#############################################################
#
# msmtp
#
############################################################

MSMTP_VERSION = 1.6.8
MSMTP_SITE = https://marlam.de/msmtp/releases
MSMTP_SOURCE = msmtp-$(MSMTP_VERSION).tar.xz

MSMTP_INSTALL_STAGING = NO
MSMTP_INSTALL_TARGET = YES
MSMTP_BINARY:=src/msmtp
MSMTP_TARGET_BINARY:=usr/bin/msmtp

MSMTP_CONF_ENV = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_MSMTP_OPTIM)" \
	CXXFLAGS="$(TARGET_CXXFLAGS) $(BR2_PACKAGE_MSMTP_OPTIM)"

MSMTP_CONF_OPT = --program-prefix="" --with-ssl=openssl --without-libidn --disable-gai-idn

MSMTP_DEPENDENCIES = uclibc openssl host-pkgconfig

$(eval $(call AUTOTARGETS,package,msmtp))
