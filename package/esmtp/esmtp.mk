#############################################################
#
# esmtp
#
#############################################################

ESMTP_VERSION = 1.2
ESMTP_SOURCE = esmtp-$(ESMTP_VERSION).tar.bz2
ESMTP_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/esmtp/esmtp/$(ESMTP_VERSION)

ESMTP_AUTORECONF = NO
ESMTP_INSTALL_STAGING = NO
ESMTP_INSTALL_TARGET = YES
ESMTP_LIBTOOL_PATCH = NO

ESMTP_DEPENDENCIES = uclibc libesmtp

$(eval $(call AUTOTARGETS,package,esmtp))
