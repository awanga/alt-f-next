#############################################################
#
# blackbox
#
#############################################################

BLACKBOX_VERSION:=0.70.1
BLACKBOX_SOURCE:=blackbox-$(BLACKBOX_VERSION).tar.bz2
BLACKBOX_SITE:=$(BR2_SOURCEFORGE_MIRROR)/sourceforge/blackboxwm/
BLACKBOX_AUTORECONF:=NO
BLACKBOX_INSTALL_STAGING:=NO
BLACKBOX_INSTALL_TARGET:=YES

BLACKBOX_CONF_OPT:=--x-includes=$(STAGING_DIR)/usr/include/X11 \
		--x-libraries=$(STAGING_DIR)/usr/lib

BLACKBOX_DEPENDENCIES:=uclibc xserver_xorg-server

$(eval $(call AUTOTARGETS,package,blackbox))
