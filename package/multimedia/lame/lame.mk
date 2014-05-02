#############################################################
#
# lame
#
#############################################################

LAME_MAJOR = 3.99
LAME_VERSION = 3.99.5
LAME_SOURCE = lame-$(LAME_VERSION).tar.gz
LAME_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/lame/lame/$(LAME_MAJOR)

LAME_AUTORECONF = NO
LAME_LIBTOOL_PATCH = NO

LAME_INSTALL_STAGING = YES
LAME_INSTALL_TARGET = YES

LAME_DEPENDENCIES = uclibc
LAME_CONF_OPT = --disable-static 

$(eval $(call AUTOTARGETS,package/multimedia,lame))
