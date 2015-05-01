#############################################################
#
# logitechmediaserver
#
#############################################################

#http://downloads.slimdevices.com/LogitechMediaServer_v7.8.0/logitechmediaserver-7.8.0-noCPAN.tgz
#https://github.com/Logitech/slimserver-vendor/archive/public/7.8.zip
# extracts to slimserver-vendor-public-7.8

LOGITECHMEDIASERVER_VERSION:=7.8
LOGITECHMEDIASERVER_SITE:=https://github.com/Logitech/slimserver-vendor/archive/public
LOGITECHMEDIASERVER_SOURCE:=logitechmediaserver-$(LOGITECHMEDIASERVER_VERSION).zip

LOGITECHMEDIASERVER_LIBTOOL_PATCH = NO
LOGITECHMEDIASERVER_INSTALL_STAGING = NO

LOGITECHMEDIASERVER_DEPENDENCIES = perl icu
LOGITECHMEDIASERVER_DEPENDENCIES_SUBDIR = CPAN

PERL_MN=$(shell perl -MConfig -le '$$Config{version} =~ /(\d+.\d+)\./; print $$1')
PERL_HOST_ARCH=$(shell perl -MConfig -e '$$Config{archname} =~ /(.*)/; print $$1')

LOGITECHMEDIASERVER_DESTDIR = $(TARGET_DIR)/usr/lib/lms
LOGITECHMEDIASERVER_CPAN = $(LOGITECHMEDIASERVER_DESTDIR)/CPAN/arch/$(PERL_MN)/arm-linux

$(eval $(call AUTOTARGETS,package,logitechmediaserver))

$(LOGITECHMEDIASERVER_TARGET_SOURCE):
	$(call DOWNLOAD,$(LOGITECHMEDIASERVER_SITE),$(LOGITECHMEDIASERVER_VERSION).zip)
	(cd $(DL_DIR); ln -sf $(LOGITECHMEDIASERVER_VERSION).zip $(LOGITECHMEDIASERVER_SOURCE))
	mkdir -p $(BUILD_DIR)/logitechmediaserver-$(LOGITECHMEDIASERVER_VERSION)
	touch $@

$(LOGITECHMEDIASERVER_TARGET_EXTRACT):
	$(call MESSAGE,"Extracting")
	(cd $(BUILD_DIR); \
		unzip $(DL_DIR)/$(LOGITECHMEDIASERVER_SOURCE); \
		mv slimserver-vendor-public-$(LOGITECHMEDIASERVER_VERSION)/* $(LOGITECHMEDIASERVER_DIR); \
		rm -rf slimserver-vendor-public-$(LOGITECHMEDIASERVER_VERSION); \
	)
	(cd $(LOGITECHMEDIASERVER_DIR_PREFIX)/multimedia/$(LOGITECHMEDIASERVER_NAME); \
		cp *.patch buildit.sh $(LOGITECHMEDIASERVER_DIR)/CPAN \
	)
	touch $@

$(LOGITECHMEDIASERVER_TARGET_CONFIGURE):
	touch $@

$(LOGITECHMEDIASERVER_TARGET_BUILD):
	(cd $(LOGITECHMEDIASERVER_DIR); \
		cd CPAN; \
		CROSS=$(GNU_TARGET_NAME) \
		CC=$(TARGET_CC) \
		CFLAGS="-pipe -fomit-frame-pointer -O2" \
		CXXFLAGS="-pipe -fomit-frame-pointer -O2" \
		ICU_HOST_DIR=$(ICU_HOST_DIR) \
		PERL_SRC=$(BUILD_DIR)/perl-5.16.0 \
		./buildit.sh; \
	)
	touch $@

$(LOGITECHMEDIASERVER_TARGET_INSTALL_TARGET):
	mkdir -p $(LOGITECHMEDIASERVER_CPAN)
	rm -f $(LOGITECHMEDIASERVER_CPAN)/auto/IO/Interface/autosplit.ix
	cp -a  $(LOGITECHMEDIASERVER_DIR)/CPAN/build/arch/$(PERL_MN)/$(PERL_HOST_ARCH)/auto $(LOGITECHMEDIASERVER_CPAN)
	cp -a $(LOGITECHMEDIASERVER_DIR)/CPAN/build/lib/libmediascan.so* $(TARGET_DIR)/usr/lib/
	touch $@
