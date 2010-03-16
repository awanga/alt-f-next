#############################################################
#
# libesmtp
#
#############################################################
LIBESMTP_VERSION = 1.0.4
LIBESMTP_SOURCE = libesmtp-$(LIBESMTP_VERSION).tar.bz2
LIBESMTP_SITE = http://www.stafford.uklinux.net/libesmtp
LIBESMTP_AUTORECONF = NO
LIBESMTP_INSTALL_STAGING = YES
LIBESMTP_INSTALL_TARGET = YES
LIBESMTP_LIBTOOL_PATCH = NO

LIBESMTP_DEPENDENCIES = uclibc openssl

$(eval $(call AUTOTARGETS,package,libesmtp))
