#############################################################
#
# parted
#
#############################################################

PARTED_VERSION:=3.2
PARTED_SOURCE:=parted-$(PARTED_VERSION).tar.xz
PARTED_SITE:=$(BR2_GNU_MIRROR)/parted

PARTED_DIR:=$(BUILD_DIR)/parted-$(PARTED_VERSION)

PARTED_INSTALL_STAGING = NO
PARTED_LIBTOOL_PATCH = NO

PARTED_DEPENDENCIES = uclibc libuuid libiconv

PARTED_CONF_OPT = --disable-device-mapper --without-readline \
	--disable-shared --disable-dynamic-loading 
	
PARTED_CONF_ENV = LIBS=-liconv

$(eval $(call AUTOTARGETS,package,parted))
