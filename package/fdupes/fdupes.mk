#############################################################
#
# fdupes
#
#############################################################

FDUPES_VERSION:=1.51
FDUPES_SOURCE:=fdupes-$(FDUPES_VERSION).tar.gz
FDUPES_SITE:=https://github.com/adrianlopezroche/fdupes/archive

FDUPES_LIBTOOL_PATCH = NO
FDUPES_AUTORECONF = NO

FDUPES_INSTALL_TARGET_OPT = PREFIX=$(TARGET_DIR)/usr install

FDUPES_MAKE_ENV = CC="$(TARGET_CC) $(TARGET_CFLAGS)"

$(eval $(call AUTOTARGETS,package,fdupes))

$(FDUPES_TARGET_CONFIGURE):
	$(SED) 's/^CC/#CC/' $(FDUPES_DIR)/Makefile
	touch $@
