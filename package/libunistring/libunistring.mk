#############################################################
#
# libunistring
#
############################################################

LIBUNISTRING_VERSION:=0.9.3
LIBUNISTRING_SITE:=$(BR2_GNU_MIRROR)/libunistring
LIBUNISTRING_SOURCE=libunistring-$(LIBUNISTRING_VERSION).tar.gz

LIBUNISTRING_LIBTOOL_PATCH = NO
LIBUNISTRING_INSTALL_STAGING = YES

LIBUNISTRING_CONF_OPT = --disable-static

$(eval $(call AUTOTARGETS,package,libunistring))
