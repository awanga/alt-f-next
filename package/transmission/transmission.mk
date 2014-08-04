#############################################################
#
# transmission
#
#############################################################

TRANSMISSION_VERSION = 2.84
TRANSMISSION_SOURCE = transmission-$(TRANSMISSION_VERSION).tar.xz
TRANSMISSION_SITE = http://download.m0k.org/transmission/files

TRANSMISSION_AUTORECONF = NO
TRANSMISSION_INSTALL_STAGING = NO
TRANSMISSION_INSTALL_TARGET = YES
TRANSMISSION_LIBTOOL_PATCH = NO

TRANSMISSION_DEPENDENCIES = uclibc libcurl openssl libevent2 pkg-config
TRANSMISSION_CONF_OPT = --disable-nls --disable-gtk --disable-gconf2 --enable-utp
TRANSMISSION_CONF_ENV = LIBEVENT_CFLAGS="-I$(STAGING_DIR)/libevent2/include" \
	LIBEVENT_LIBS="-L$(STAGING_DIR)/libevent2/lib -levent2" ac_cv_prog_HAVE_CXX=yes

$(eval $(call AUTOTARGETS,package,transmission))
