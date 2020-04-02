#############################################################
#
# amule
#
#############################################################

AMULE_VERSION:=2.3.2
AMULE_SOURCE:=aMule-$(AMULE_VERSION).tar.bz2
AMULE_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/amule/aMule/$(AMULE_VERSION)

AMULE_LIBTOOL_PATCH = NO
AMULE_AUTORECONF = YES

AMULE_DEPENDENCIES = wxwidgets cryptopp libupnp libpng readline

AMULE_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

AMULE_CONF_OPT = --enable-optimize \
	--with-wx-prefix=$(STAGING_DIR)/usr --with-crypto-prefix=$(STAGING_DIR)/usr \
	--with-gdlib-prefix=$(STAGING_DIR)/usr --disable-monolithic --disable-amule-gui \
	--disable-wxcas --enable-cas --disable-alc --enable-alcc \
	--enable-fileview --enable-xas --enable-amulecmd --enable-amule-daemon --enable-webserver

$(eval $(call AUTOTARGETS,package,amule))

$(AMULE_HOOK_POST_CONFIGURE):
	$(SED) 's/^cas_CFLAGS.*/& -D_GNU_SOURCE/' $(AMULE_DIR)/src/utils/cas/Makefile

$(AMULE_HOOK_POST_EXTRACT):
	# make autoreconf not fail
	(cd $(AMULE_DIR); touch NEWS README AUTHORS ChangeLog)
	# enable embedding using Alt-F webUI iframe
	$(SED) 's|breakout_of_frame();|//breakout_of_frame();|' $(AMULE_DIR)/src/webserver/default/login.php
