#############################################################
#
# cryptopp
#
#############################################################

CRYPTOPP_VERSION:=5.6.5
CRYPTOPP_VERSION2:=5_6_5

CRYPTOPP_SOURCE:=CRYPTOPP_$(CRYPTOPP_VERSION2).tar.gz
CRYPTOPP_SITE:=https://github.com/weidai11/cryptopp/archive

CRYPTOPP_LIBTOOL_PATCH = NO
CRYPTOPP_INSTALL_STAGING = YES

CRYPTOPP_MAKE_OPT = dynamic # cryptest.exe

CRYPTOPP_MAKE_ENV = \
	CC="$(TARGET_CC)" \
	CXX="$(TARGET_CXX)" \
	CXXFLAGS="$(TARGET_CXXFLAGS) -DNDEBUG -fPIC" \
	AR=$(TARGET_AR) \
	LD=$(TARGET_LD) \
	STRIP=$(TARGET_STRIP)
	RANLIB=$(TARGET_RANLIB)

CRYPTOPP_INSTALL_TARGET_OPT = PREFIX=$(TARGET_DIR)/usr install
CRYPTOPP_INSTALL_STAGING_OPT = PREFIX=$(STAGING_DIR)/usr install

$(eval $(call AUTOTARGETS,package,cryptopp))

$(CRYPTOPP_TARGET_CONFIGURE):
	$(SED) 's/\(.*march=native\)/#\1/' \
	-e 's|./libcryptopp.a|-L. -lcryptopp|' $(CRYPTOPP_DIR)/GNUmakefile
	touch $@

