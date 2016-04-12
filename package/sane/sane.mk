#############################################################
#
# sane
#
#############################################################

SANE_VERSION = 1.0.21

# alioth.debian.org is requesting login to download?!
#SANE_SOURCE = sane-backends-$(SANE_VERSION).tar.gz
#SANE_SITE = http://alioth.debian.org/frs/download.php/file/3258
#SANE_WGET_OPTS = --no-check-certificate

SANE_SOURCE = sane-backends_$(SANE_VERSION).orig.tar.gz
SANE_SITE = http://archive.debian.org/debian/pool/main/s/sane-backends

SANE_AUTORECONF = NO
SANE_LIBTOOL_PATCH = YES

SANE_INSTALL_STAGING = YES
SANE_INSTALL_TARGET = YES

SANE_DEPENDENCIES = uclibc libusb jpeg tiff

SANE_CONF_OPT = --disable-latex --disable-translations $(DISABLE_IPV6) --disable-avahi --disable-rpath --with-pic --without-gphoto2

$(eval $(call AUTOTARGETS,package,sane))

$(SANE_HOOK_POST_INSTALL):
	sed -i 's|^includedir=.*|includedir="$(STAGING_DIR)/usr/include"|'  $(STAGING_DIR)/usr/bin/sane-config
	sed -i 's|^libdir=.*|libdir="$(STAGING_DIR)/usr/lib"|' $(STAGING_DIR)/usr/bin/sane-config
	touch $@
