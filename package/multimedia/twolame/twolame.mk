#############################################################
#
# twolame
#
#############################################################

TWOLAME_VERSION = 0.3.13
TWOLAME_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/twolame/twolame/$(TWOLAME_VERSION)
TWOLAME_SOURCE = twolame-$(TWOLAME_VERSION).tar.gz

TWOLAME_AUTORECONF = NO
TWOLAME_INSTALL_STAGING = YES
TWOLAME_INSTALL_TARGET = YES
TWOLAME_LIBTOOL_PATCH = NO

$(eval $(call AUTOTARGETS,package,twolame))

