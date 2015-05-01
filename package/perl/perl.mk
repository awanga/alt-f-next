#############################################################
#
# perl
#
#############################################################

PERL_MAJOR:=5
PERL_VERSION:=5.16.0
PERL_SOURCE:=perl-$(PERL_VERSION).tar.gz
PERL_SITE:=http://www.cpan.org/src/$(PERL_MAJOR).0
PERL_DIR:=$(BUILD_DIR)/perl-$(PERL_VERSION)
PERL_CAT:=$(ZCAT)

PERL_CROSS_VERSION=0.7.1
PERL_CROSS_SOURCE=perl-$(PERL_VERSION)-cross-$(PERL_CROSS_VERSION).tar.gz
PERL_CROSS_SITE=$(BR2_SOURCEFORGE_MIRROR)/project/perlcross.berlios

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

# When using threads, perl uses a dynamically-sized buffer for some of
# the thread-safe library calls, such as those in the getpw*() family.
# This buffer starts small, but it will keep growing until the result
# fits.  To get a fixed upper limit, you should compile Perl with
# PERL_REENTRANT_MAXSIZE defined to be the number of bytes you want.  One
# way to do this is to run Configure with
#   -Accflags=-DPERL_REENTRANT_MAXSIZE=65536

$(PERL_DIR)/.stamp_configured: $(PERL_DIR)/.stamp_cross
	( \
	cd $(PERL_DIR); \
	./configure \
	--prefix=/usr \
	--target=arm-linux-uclibc \
	--target-tools-prefix=arm-linux- \
	-Accflags="$(TARGET_CFLAGS)" \
	-Duseopcode -Dusethreads \
	)
	touch $@

$(PERL_DIR)/.stamp_build: $(PERL_DIR)/.stamp_configured
	$(MAKE1) -C $(PERL_DIR) # there is a non-tracked dependency, don't parallel
	touch $@

$(PERL_DIR)/.stamp_installed: $(PERL_DIR)/.stamp_build
	$(MAKE1) -C $(PERL_DIR) DESTDIR=$(STAGING_DIR) install.perl
	$(MAKE1) -C $(PERL_DIR) DESTDIR=$(TARGET_DIR) install.perl
	chmod +w $(TARGET_DIR)/usr/lib/perl/arm-linux/Config.pm $(TARGET_DIR)/usr/lib/perl/arm-linux/Config_heavy.pl
	sed -i "s/cc *=> *'arm-linux-gcc'/cc => 'gcc'/" $(TARGET_DIR)/usr/lib/perl/arm-linux/Config.pm
	sed -i -e "s/'arm-linux-\(.*\)'/'\1'/" \
		-e "s/myuname='uclibc'/myuname='arm-linux-uclibc'/" \
		-e "s|-I/.*include ||" \
		-e "s|--sysroot=.*staging_dir/ ||" \
		-e "s|-isysroot.*staging_dir ||" \
		$(TARGET_DIR)/usr/lib/perl/arm-linux/Config_heavy.pl
	touch $@

#####################
# perl for the host

PERL_HOST_INSTALL_OPT = install.perl

$(eval $(call AUTOTARGETS_HOST,package,perl))

$(PERL_HOST_CONFIGURE):
	( cd $(PERL_HOST_DIR); ./configure.gnu --prefix=$(HOST_DIR)/usr )
	touch $@

#####################

perl-source: $(DL_DIR)/$(PERL_SOURCE)

perl-extract: $(PERL_DIR)/.stamp_extracted

perl-configure: $(PERL_DIR)/.stamp_configured

perl-build: $(PERL_DIR)/.stamp_build

perl: uclibc gdbm perl-host $(PERL_DIR)/.stamp_installed

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_PERL),y)
TARGETS+=perl
endif
