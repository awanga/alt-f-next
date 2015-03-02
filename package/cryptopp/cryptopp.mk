#############################################################
#
# cryptopp
#
#############################################################

CRYPTOPP_VERSION:=562
CRYPTOPP_VERSION2:=5.6.2
CRYPTOPP_SOURCE:=cryptopp$(CRYPTOPP_VERSION).zip
CRYPTOPP_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/cryptopp/cryptopp/$(CRYPTOPP_VERSION2)

CRYPTOPP_LIBTOOL_PATCH = NO
CRYPTOPP_INSTALL_STAGING = YES

CRYPTOPP_MAKE_OPT = dynamic

CRYPTOPP_MAKE_ENV = \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	CXXFLAGS="$(TARGET_CXXFLAGS) -fPIC" \
	AR=$(TARGET_AR) \
	LD=$(TARGET_LD) \
	STRIP=$(TARGET_STRIP)
	RANLIB=$(TARGET_RANLIB)

CRYPTOPP_INSTALL_TARGET_OPT = PREFIX=$(TARGET_DIR)/usr install
CRYPTOPP_INSTALL_STAGING_OPT = PREFIX=$(STAGING_DIR)/usr install

$(eval $(call AUTOTARGETS,package,cryptopp))

$(CRYPTOPP_TARGET_EXTRACT):
	if ! which unzip; then /bin/echo -e "\n\nYou must install 'unzip' on your build machine\n"; fi
	unzip -a $(DL_DIR)/$(CRYPTOPP_SOURCE) -d $(CRYPTOPP_DIR)
	sed -i 's/\(.*march=native\)/#\1/' $(CRYPTOPP_DIR)/GNUmakefile
	touch $@

$(CRYPTOPP_TARGET_CONFIGURE):
	touch $@

