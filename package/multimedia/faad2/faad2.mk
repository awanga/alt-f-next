################################################################################
#
# faad2
#
################################################################################

FAAD2_VERSION = 2.7
FAAD2_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/faac/faad2-src/faad2-$(FAAD2_VERSION)
FAAD2_SOURCE = faad2-$(FAAD2_VERSION).tar.bz2

FAAD2_AUTORECONF = NO
FAAD2_LIBTOOL_PATCH = NO

FAAD2_INSTALL_STAGING = YES
FAAD2_CONF_ENV = LIBS="-lm"

$(eval $(call AUTOTARGETS,package/multimedia,faad2))
