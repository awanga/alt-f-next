#############################################################
#
# transmission
#
#############################################################

TRANSMISSION_VERSION = 2.84
TRANSMISSION_SOURCE = transmission-$(TRANSMISSION_VERSION).tar.xz
TRANSMISSION_SITE = http://download.m0k.org/transmission/files

TRANSMISSION_AUTORECONF = NO
TRANSMISSION_LIBTOOL_PATCH = NO

TRANSMISSION_DEPENDENCIES = uclibc libcurl openssl libevent2 pkg-config
TRANSMISSION_CONF_OPT = --disable-nls --disable-gtk --disable-gconf2 --enable-utp

$(eval $(call AUTOTARGETS,package,transmission))
