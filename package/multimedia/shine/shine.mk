################################################################################
#
# shine
#
################################################################################

SHINE_VERSION = 3.1.0
SHINE_SOURCE = shine-$(SHINE_VERSION).tar.gz
SHINE_SITE = https://github.com/savonet/shine/releases/download/$(SHINE_VERSION)

SHINE_AUTORECONF = NO
SHINE_LIBTOOL_PATCH = NO

SHINE_CONF_OPT = --disable-shared

$(eval $(call AUTOTARGETS,package/multimedia,shine))
