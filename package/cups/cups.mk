############################################################
#
# cups
#
############################################################

#CUPS_VERSION = 1.7.5 works, but cups-filters is needed: 
# http://www.linuxfoundation.org/collaborate/workgroups/openprinting/cups-filters

CUPS_VERSION = 1.4.8
CUPS_NAME = cups-$(CUPS_VERSION)
CUPS_SOURCE:=$(CUPS_NAME)-source.tar.bz2
CUPS_SITE = https://www.cups.org/software/$(CUPS_VERSION)

CUPS_CAT:=$(BZCAT)
CUPS_DIR = $(BUILD_DIR)/$(CUPS_NAME)
CUPS_DESTDIR:=$(STAGING_DIR)/usr/lib
CUPS_MAKE_ENV = STRIPPROG=arm-linux-strip

CUPS_TARGET_BINARY:=usr/sbin/cupsd
CUPS_DEPENDENCIES = uclibc openssl libusb dbus avahi libpng jpeg tiff host-autoconf

ifeq ($(BR2_PACKAGE_DBUS),y)
	CUPS_CONF_OPT += --enable-dbus
	CUPS_DEPENDENCIES += dbus
else
	CUPS_CONF_OPT += --disable-dbus
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
	CUPS_DEPENDENCIES += xlib_libX11
endif

CUPS_CONF_OPT +=	--disable-perl
CUPS_CONF_OPT +=	--disable-java
CUPS_CFLAGS = $(TARGET_CFLAGS)

ifeq ($(BR2_PACKAGE_PERL),disabled)	# We do not provide perl (yet)
	CUPS_CONF_ENV +=	ac_cv_path_perl=$(STAGING_DIR)/usr/bin/perl
	CUPS_CONF_OPT +=	--with-perl
	CUPS_DEPENDENCIES +=	microperl
else
	CUPS_CONF_OPT +=	--disable-perl
endif

# disable PHP
#ifeq ($(BR2_PACKAGE_PHP),y)
ifeq ($(BR2_PACKAGE_PHP),foo)
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/php
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/php/main
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/php/regex
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/php/TSRM
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/php/Zend
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/php/ext
	CUPS_CONF_ENV +=	ac_cv_path_php=$(STAGING_DIR)/usr/bin/php
	CUPS_CONF_OPT +=	--with-php
	CUPS_DEPENDENCIES +=	php
else
	CUPS_CONF_OPT +=	--disable-php
endif

ifeq ($(BR2_PACKAGE_PYTHON),y)
	CUPS_CFLAGS += 		-I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)
	CUPS_CONF_ENV +=	ac_cv_path_python=$(STAGING_DIR)/usr/bin/python
	CUPS_CONF_OPT +=	--with-python
	CUPS_DEPENDENCIES +=	python
else
	CUPS_CONF_OPT +=	--disable-python
endif

ifeq ($(BR2_PACKAGE_CUPS_PDFTOPS),y)
	CUPS_CONF_OPT += --enable-pdftops
else
	CUPS_CONF_OPT += --disable-pdftops
endif

$(DL_DIR)/$(CUPS_SOURCE):
	 $(call DOWNLOAD,$(CUPS_SITE),$(CUPS_SOURCE))

$(CUPS_DIR)/.unpacked: $(DL_DIR)/$(CUPS_SOURCE)
	$(CUPS_CAT) $(DL_DIR)/$(CUPS_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(CUPS_DIR) package/cups/ \*.patch
	$(CONFIG_UPDATE) $(CUPS_DIR)
	touch $@

CUPS_CONF_OPT = --without-perl --without-java --without-php --without-python \
	--disable-pam --disable-dnssd --disable-ldap \
	--disable-gnutls --disable-gssapi --disable-acl --disable-dbus \
	--with-cups-user=cups --with-cups-group=lpadmin --with-system_groups="sys root" \
	--enable-openssl --enable-libusb --with-pdftops=/usr/bin/gs \
	--with-languages=none --with-docdir=/usr/share/cups/doc

#		CFLAGS="$(CUPS_CFLAGS)" \

$(CUPS_DIR)/.configured: $(CUPS_DIR)/.unpacked
	cd $(CUPS_DIR) && $(AUTOCONF)
	(cd $(CUPS_DIR) && \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		$(CUPS_CONF_ENV) \
		./configure \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--exec-prefix=/usr \
		--libdir=/usr/lib \
		--sysconfdir=/etc \
		--localstatedir=/var \
		--with-icondir=/usr/share/icons \
		--disable-gnutls \
		--disable-gssapi \
		$(CUPS_CONF_OPT) \
		)
	touch $@

# cups backend berkeley cgi-bin filter \
#	locale monitor notifier pdftops scheduler systemv scripting/php \
#	conf data doc fonts ppd templates

$(CUPS_DIR)/.compiled: $(CUPS_DIR)/.configured
	#$(MAKE) CFLAGS="$(CUPS_CFLAGS)" -C $(CUPS_DIR)
	$(MAKE) -C $(CUPS_DIR)
	touch $@

$(TARGET_DIR)/$(CUPS_TARGET_BINARY): $(CUPS_DIR)/.compiled
	-rm -rf $(STAGING_DIR)/usr/share/cups/mime $(TARGET_DIR)/usr/share/cups/mime
	$(MAKE) -C $(CUPS_DIR) $(CUPS_MAKE_ENV) DESTDIR=$(STAGING_DIR) DSTROOT=$(STAGING_DIR) install
	$(MAKE) -C $(CUPS_DIR) $(CUPS_MAKE_ENV) DESTDIR=$(TARGET_DIR) DSTROOT=$(TARGET_DIR) install
	$(SED) "s,^prefix=.*,prefix=\'$(STAGING_DIR)/usr\',g" $(STAGING_DIR)/usr/bin/cups-config
	$(SED) "s,^exec_prefix=.*,exec_prefix=\'$(STAGING_DIR)/usr\',g" $(STAGING_DIR)/usr/bin/cups-config
	$(SED) "s,^includedir=.*,includedir=\'$(STAGING_DIR)/usr/include\',g" $(STAGING_DIR)/usr/bin/cups-config
	$(SED) "s,^libdir=.*,libdir=\'$(STAGING_DIR)/usr/lib\',g" $(STAGING_DIR)/usr/bin/cups-config
	(cd $(TARGET_DIR); \
	rm -rf ./etc/rc?.d ./etc/xinetd.d ./etc/cups/*.conf.* ./etc/dbus-1/system.d/cups.conf \
		./etc/init.d/cups ./usr/share/applications/; \
	cp -f ./usr/share/cups/charmaps/iso-8859-1.txt \
		./usr/share/cups/charmaps/us-ascii.txt; \
	)
	touch $@

cups: $(CUPS_DEPENDENCIES) $(TARGET_DIR)/$(CUPS_TARGET_BINARY)

cups-install: $(TARGET_DIR)/$(CUPS_TARGET_BINARY)

cups-build: $(CUPS_DIR)/.compiled

cups-configure: $(CUPS_DIR)/.configured

cups-extract: $(CUPS_DIR)/.unpacked

cups-source: $(DL_DIR)/$(CUPS_SOURCE)

cups-clean:
	-$(MAKE) -C $(CUPS_DIR) clean

cups-dirclean:
	rm -fr $(CUPS_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_CUPS),y)
TARGETS+=cups
endif

