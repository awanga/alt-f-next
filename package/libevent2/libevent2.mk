#############################################################
#
# libevent2
#
#############################################################

LIBEVENT2_MAJOR:=2.1
LIBEVENT2_VERSION:=2.1.5
LIBEVENT2_SOURCE:=libevent-$(LIBEVENT2_VERSION)-beta.tar.gz
LIBEVENT2_SITE:=https://github.com/libevent/libevent/releases/download/release-2.1.5-beta

LIBEVENT2_LIBTOOL_PATCH = NO
LIBEVENT2_INSTALL_STAGING = YES

LIBEVENT2_CONF_OPT = --disable-static --disable-openssl --disable-thread-support

$(eval $(call AUTOTARGETS,package,libevent2))
