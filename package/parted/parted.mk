#############################################################
#
# parted
#
#############################################################
PARTED_VERSION:=2.2
PARTED_SOURCE:=parted-$(PARTED_VERSION).tar.gz
PARTED_SITE:=$(BR2_GNU_MIRROR)/parted
PARTED_DIR:=$(BUILD_DIR)/parted-$(PARTED_VERSION)
PARTED_INSTALL_STAGING = NO
PARTED_LIBTOOL_PATCH = NO

PARTED_DEPENDENCIES = uclibc libuuid

PARTED_CONF_OPT = --disable-device-mapper --disable-dynamic-loading --without-readline --disable-shared

$(eval $(call AUTOTARGETS,package,parted))
