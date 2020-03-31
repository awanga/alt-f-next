#############################################################
#
# p7zip
#
#############################################################

P7ZIP_VERSION:=16.02
P7ZIP_SOURCE:=p7zip_$(P7ZIP_VERSION)_src_all.tar.bz2
P7ZIP_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/p7zip/p7zip/$(P7ZIP_VERSION)

P7ZIP_DEPENDENCIES = uclibc

P7ZIP_MAKE_ENV = P7ZIP_CC="$(TARGET_CC) $(TARGET_CFLAGS)" \
	P7ZIP_CXX="$(TARGET_CXX) $(TARGET_CXXFLAGS)"

P7ZIP_MAKE_OPT = all3

P7ZIP_INSTALL_TARGET_OPT = DEST_HOME=$(TARGET_DIR)/usr install

$(eval $(call AUTOTARGETS,package,p7zip))

$(P7ZIP_TARGET_CONFIGURE):
	(	cd $(P7ZIP_DIR); \
		cp makefile.linux_cross_arm makefile.machine; \
		$(SED) 's|^CC=.*|CC=$$(P7ZIP_CC) $$(ALLFLAGS)|' \
			-e 's|^CXX=.*|CXX=$$(P7ZIP_CXX) $$(ALLFLAGS)|' makefile.machine; \
		$(SED) 's|444|644|' -e 's|555|755|' \
			-e 's|echo.*DEST_SHARE.*prg}\\"|echo "/usr/lib/p7zip/$${prg}|' install.sh; \
	)
	touch $@
