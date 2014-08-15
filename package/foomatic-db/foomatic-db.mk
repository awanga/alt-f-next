#############################################################
#
# foomatic-db
#
#############################################################

##########################################
#
# foomatic-db has to be build before hplip
#
##########################################

# the database. we only need to download and extract it
FOOMATIC_DB_VERSION = 4.0
FOOMATIC_DB_SOURCE = foomatic-db-$(FOOMATIC_DB_VERSION)-current.tar.gz
FOOMATIC_DB_SITE = http://www.openprinting.org/download/foomatic/
FOOMATIC_DB_DIR = $(BUILD_DIR)/foomatic-db-$(FOOMATIC_DB_VERSION)-current

$(DL_DIR)/$(FOOMATIC_DB_SOURCE):
	$(call DOWNLOAD,$(FOOMATIC_DB_SITE),$(FOOMATIC_DB_SOURCE))

$(FOOMATIC_DB_DIR)/.unpacked: $(DL_DIR)/$(FOOMATIC_DB_SOURCE)
	mkdir -p $(FOOMATIC_DB_DIR)
	$(ZCAT) $(DL_DIR)/$(FOOMATIC_DB_SOURCE) | tar $(TAR_STRIP_COMPONENTS)=1 -C $(FOOMATIC_DB_DIR) $(TAR_OPTIONS) -
	touch $@

# the real thing, foomatic-db-engine
FOOMATIC_DB_ENGINE_VERSION = 4.0.4
FOOMATIC_DB_ENGINE_SOURCE = foomatic-db-engine-$(FOOMATIC_DB_ENGINE_VERSION).tar.gz
FOOMATIC_DB_ENGINE_SITE = http://www.openprinting.org/download/foomatic/

FOOMATIC_DB_ENGINE_LIBTOOL_PATCH = NO
FOOMATIC_DB_ENGINE_INSTALL_STAGING = NO
FOOMATIC_DB_ENGINE_INSTALL_TARGET = NO

FOOMATIC_DB_ENGINE_DIR = $(BUILD_DIR)/foomatic-db-engine-$(FOOMATIC_DB_ENGINE_VERSION)

TARGET_PPD_DIR = usr/share/ppd

$(DL_DIR)/$(FOOMATIC_DB_ENGINE_SOURCE):
	$(call DOWNLOAD,$(FOOMATIC_DB_ENGINE_SITE),$(FOOMATIC_DB_ENGINE_SOURCE))

$(FOOMATIC_DB_ENGINE_DIR)/.unpacked: $(DL_DIR)/$(FOOMATIC_DB_ENGINE_SOURCE)
	$(ZCAT) $(DL_DIR)/$(FOOMATIC_DB_ENGINE_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(FOOMATIC_DB_ENGINE_DIR)/.configured: $(FOOMATIC_DB_ENGINE_DIR)/.unpacked $(FOOMATIC_DB_DIR)/.unpacked
	(cd $(FOOMATIC_DB_ENGINE_DIR); \
		$(SED) 's/$$(CC).*foomatic-perl-data.c/& $$(XML_LIBS)/' Makefile.in; \
		$(HOST_CONFIGURE_OPTS) \
		$(HOST_CONFIGURE_ENV) \
		./configure \
	)
	touch $@

$(FOOMATIC_DB_ENGINE_DIR)/.build: $(FOOMATIC_DB_ENGINE_DIR)/.configured
	$(MAKE) -C $(FOOMATIC_DB_ENGINE_DIR) inplace
	touch $@

$(FOOMATIC_DB_ENGINE_DIR)/.dbcompiled: $(FOOMATIC_DB_ENGINE_DIR)/.build
	(cd $(FOOMATIC_DB_ENGINE_DIR); \
		./foomatic-compiledb -t ppd -j 4 -f; \
	)
	touch $@

$(FOOMATIC_DB_ENGINE_DIR)/.installed: $(FOOMATIC_DB_ENGINE_DIR)/.dbcompiled
	(cd $(FOOMATIC_DB_ENGINE_DIR); \
		mnf=$$(ls ppd | cut -d'-' -f1 | sort -u); \
		for i in $$mnf; do \
			mkdir -p $(TARGET_DIR)/$(TARGET_PPD_DIR)/$$i; \
			echo "Copying and compressing $$i printers PPD"; \
			for j in $$(ls ppd/$$i-*); do \
				nf=$$(echo $$j | cut --complement -d'-' -f1 ).gz; \
				gzip -c $$j > $(TARGET_DIR)/$(TARGET_PPD_DIR)/$$i/$$nf; \
			done \
		done \
	)
	touch $@

foomatic-db-configure: $(FOOMATIC_DB_ENGINE_DIR)/.configured
	
foomatic-db-build: $(FOOMATIC_DB_ENGINE_DIR)/.build

foomatic-db-install: $(FOOMATIC_DB_ENGINE_DIR)/.installed
	
foomatic-db: uclibc libxml2-host foomatic-filters foomatic-db-install

ifeq ($(BR2_PACKAGE_FOOMATIC_DB),y)
TARGETS+=foomatic-db
endif
