#############################################################
#
# libunistring
#
#############################################################

LIBUNISTRING_VERSION:=0.9.3
LIBUNISTRING_DIR=$(BUILD_DIR)/libavl-$(LIBUNISTRING_VERSION)
LIBUNISTRING_SITE:=http://ftp.gnu.org/gnu/libunistring/
LIBUNISTRING_SOURCE=libunistring-$(LIBUNISTRING_VERSION).tar.gz
LIBUNISTRING_LIBTOOL_PATCH = NO
LIBUNISTRING_INSTALL_STAGING = YES

#LIBUNISTRING_CONF_OPT = --disable-static --program-prefix=""

$(eval $(call AUTOTARGETS,package,libunistring))