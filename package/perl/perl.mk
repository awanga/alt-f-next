#############################################################
#
# perl
#
#############################################################
PERL_MAJOR:=5
#PERL_VERSION:=$(PERL_MAJOR).16.0
PERL_VERSION:=5.16.0
PERL_SOURCE:=perl-$(PERL_VERSION).tar.gz
PERL_SITE:=http://www.cpan.org/src/$(PERL_MAJOR).0/
PERL_DIR:=$(BUILD_DIR)/perl-$(PERL_VERSION)
PERL_CAT:=$(ZCAT)

PERL_CROSS_VERSION=0.7
PERL_CROSS_SOURCE=perl-$(PERL_VERSION)-cross-$(PERL_CROSS_VERSION).tar.gz
PERL_CROSS_SITE=http://download.berlios.de/perlcross

$(DL_DIR)/$(PERL_CROSS_SOURCE):
	$(call DOWNLOAD,$(PERL_CROSS_SITE),$(PERL_CROSS_SOURCE))

$(DL_DIR)/$(PERL_SOURCE): $(DL_DIR)/$(PERL_CROSS_SOURCE)
	$(call DOWNLOAD,$(PERL_SITE),$(PERL_SOURCE))

$(PERL_DIR)/.stamp_extracted: $(DL_DIR)/$(PERL_SOURCE)
	$(PERL_CAT) $(DL_DIR)/$(PERL_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(PERL_DIR)/.stamp_cross: $(PERL_DIR)/.stamp_extracted
	tar -C $(PERL_DIR)/.. -xzf $(DL_DIR)/$(PERL_CROSS_SOURCE)
	chmod -R ug+rw $(PERL_DIR)
	touch $@

$(PERL_DIR)/.stamp_configured: $(PERL_DIR)/.stamp_cross
	( \
	cd $(PERL_DIR); \
	./configure \
	--prefix=/usr \
	--target=arm-linux-uclibc \
	--target-tools-prefix=arm-linux- \
	-Accflags="$(TARGET_CFLAGS)" \
	-Duseopcode \
	)
	touch $@

$(PERL_DIR)/.stamp_build: $(PERL_DIR)/.stamp_configured
	#$(MAKE) -C $(PERL_DIR) # there is a non-tracked dependency, don't parallel
	make -C $(PERL_DIR)
	touch $@

$(PERL_DIR)/.stamp_installed: $(PERL_DIR)/.stamp_build
	make -C $(PERL_DIR) DESTDIR=$(TARGET_DIR) install.perl

perl-source: $(DL_DIR)/$(PERL_SOURCE)

perl-extract: $(PERL_DIR)/.stamp_extracted

perl-configure: $(PERL_DIR)/.stamp_configured

perl-build: $(PERL_DIR)/.stamp_build

perl: $(PERL_DIR)/.stamp_installed

#perl-: $(PERL_DIR)/.stamp_

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_PERL),y)
TARGETS+=perl
endif
