#############################################################
#
# transmission
#
#############################################################

TRANSMISSION_VERSION = 2.22
TRANSMISSION_SOURCE = transmission-$(TRANSMISSION_VERSION).tar.bz2
TRANSMISSION_SITE = http://download.m0k.org/transmission/files
TRANSMISSION_AUTORECONF = NO
TRANSMISSION_INSTALL_STAGING = NO
TRANSMISSION_INSTALL_TARGET = YES
TRANSMISSION_LIBTOOL_PATCH = NO
TRANSMISSION_CONF_OPT = --disable-nls --disable-gtk --disable-gconf2

TRANSMISSION_DEPENDENCIES = uclibc libcurl openssl libevent pkg-config

$(eval $(call AUTOTARGETS,package,transmission))
