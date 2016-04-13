#############################################################
#
# php
#
#############################################################

PHP_SITE = http://php.net/distributions
PHP_VERSION = 5.4.34

PHP_SOURCE = php-$(PHP_VERSION).tar.bz2
PHP_INSTALL_STAGING = YES
PHP_INSTALL_STAGING_OPT = INSTALL_ROOT=$(STAGING_DIR) install
PHP_INSTALL_TARGET_OPT = INSTALL_ROOT=$(TARGET_DIR) install
PHP_LIBTOOL_PATCH = NO
PHP_DEPENDENCIES = uclibc

PHP_CONF_ENV = ac_cv_func_dlopen=yes \
	ac_cv_lib_dl_dlopen=yes \
	ac_cv_func_libiconv=yes \
	ac_cv_pthreads_lib=-lpthread \
	EXTENSION_DIR=/usr/lib/php5/extensions \
	EXTRA_LIBS=-lpthread

PHP_CONF_OPT = $(DISABLE_IPV6) \
		--mandir=/usr/share/man \
		--infodir=/usr/share/info \
		--program-transform-name='' \
		--with-config-file-path=/etc \
		--localstatedir=/var \
		--disable-all \
		--without-pear \
		--with-zlib-dir=${STAGING_DIR}/usr \
		--with-jpeg-dir=${STAGING_DIR}/usr \
		--with-png-dir=${STAGING_DIR}/usr \
		--with-openssl-dir=${STAGING_DIR}/usr \
		--with-libxml-dir=${STAGING_DIR}/usr \

ifneq ($(BR2_PACKAGE_PHP_CLI),y)
	PHP_CONF_OPT += --disable-cli
else
	PHP_CONF_OPT += --enable-cli
endif

ifneq ($(BR2_PACKAGE_PHP_CGI),y)
	PHP_CONF_OPT += --disable-cgi
else
	PHP_CONF_OPT += --enable-cgi
endif

### Extensions

ifeq ($(BR2_PACKAGE_PHP_EXT_PHAR),y)
	PHP_CONF_OPT += --enable-phar=shared,${STAGING_DIR}/usr
	PHP_DEPENDENCIES += zlib bzip2
	# FIXME:php-hosthost should be build with phar extension enabled, cross-compiling phar extension needs it
	PHP_MAKE_OPT = PHP_EXECUTABLE=/usr/bin/php
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_LIBICONV),y)
	PHP_CONF_OPT += --with-iconv=shared,${STAGING_DIR}/usr
	PHP_DEPENDENCIES += libiconv
endif

# PHP has its own version of libgd! Better if they changed its name!
ifeq ($(BR2_PACKAGE_PHP_EXT_GD),y)
	PHP_CONF_OPT += --with-gd=shared
	PHP_DEPENDENCIES += libpng
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_MCRYPT),y)
	PHP_CONF_OPT += --with-mcrypt=shared,${STAGING_DIR}/usr
	PHP_DEPENDENCIES += libmcrypt
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_CURL),y)
	PHP_CONF_OPT += --with-curl=shared,${STAGING_DIR}/usr
	PHP_DEPENDENCIES += libcurl
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_CTYPE),y)
	PHP_CONF_OPT += --enable-ctype=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_FILEINFO),y)
	PHP_CONF_OPT += --enable-fileinfo=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SNMP),y)
	# when using /usr/lib/libnetsnmp.so.20.0.1 lots of tests fail
	PHP_CONF_OPT += --with-snmp=shared,$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += netsnmp
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_MBSTRING),y)
	PHP_CONF_OPT += --enable-mbstring=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_DOM),y)
	PHP_CONF_OPT += --enable-dom=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_HASH),y)
	PHP_CONF_OPT += --enable-hash=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_TOKENIZER),y)
	PHP_CONF_OPT += --enable-tokenizer=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SOAP),y)
	PHP_CONF_OPT += --enable-soap=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SOCKETS),y)
	PHP_CONF_OPT += --enable-sockets=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_POSIX),y)
	PHP_CONF_OPT += --enable-posix=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SESSION),y)
	PHP_CONF_OPT += --enable-session=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_OPENSSL),y)
	PHP_CONF_OPT += --with-openssl=shared,$(STAGING_DIR)/usr  
	PHP_DEPENDENCIES += openssl
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_LIBXML2),y)
	PHP_CONF_OPT += --enable-libxml=shared \
		--enable-xml=shared \
		--enable-xmlreader=shared \
		--enable-xmlwriter=shared
	PHP_DEPENDENCIES += libxml2
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SIMPLEXML),y)
	PHP_CONF_OPT += --enable-simplexml=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_ZLIB),y)
	PHP_CONF_OPT += --with-zlib=shared,$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += zlib
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_EXIF),y)
	PHP_CONF_OPT += --enable-exif=shared
	PHP_DEPENDENCIES += libexif
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_FTP),y)
	PHP_CONF_OPT += --enable-ftp=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_GETTEXT),y)
	PHP_CONF_OPT += --with-gettext=$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += gettext
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_GMP),y)
	PHP_CONF_OPT += --with-gmp=$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += libgmp
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_JSON),y)
	PHP_CONF_OPT += --enable-json=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_READLINE),y)
	PHP_CONF_OPT += --with-readline=shared,$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += readline
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SYSVMSG),y)
	PHP_CONF_OPT += --enable-sysvmsg=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SYSVSEM),y)
	PHP_CONF_OPT += --enable-sysvsem=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_SYSVSHM),y)
	PHP_CONF_OPT += --enable-sysvshm=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_ZIP),y)
	PHP_CONF_OPT += --enable-zip=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_BZIP2),y)
	PHP_CONF_OPT += --with-bz2=shared,$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += bzip2
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_FILTER),y)
	PHP_CONF_OPT += --enable-filter=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_CALENDAR),y)
	PHP_CONF_OPT += --enable-calendar=shared
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_PCRE),y)
	PHP_CONF_OPT += --with-pcre-regex
endif

# PHP segfaults if linked agains a threadsafe compiled sqlite!
# and it also segfaults when mysql is enabled!

ifeq ($(BR2_PACKAGE_PHP_EXT_SQLITE),y)
	#PHP_CONF_ENV += CFLAGS+=" -DSQLITE_OMIT_LOAD_EXTENSION -DSQLITE_ENABLE_UNLOCK_NOTIFY"
	PHP_CONF_OPT += --with-sqlite3=shared,$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += sqlite
endif

ifeq ($(BR2_PACKAGE_PHP_EXT_MYSQL),y)
	PHP_CONF_OPT += --with-mysql=shared,$(STAGING_DIR)/usr
	PHP_DEPENDENCIES += mysql
endif

### PDO
# see above comment regarding sqlite
ifeq ($(BR2_PACKAGE_PHP_EXT_PDO),y)
	PHP_CONF_OPT += --enable-pdo=shared

	ifeq ($(BR2_PACKAGE_PHP_EXT_PDO_SQLITE),y)
		ifeq ($(BR2_PACKAGE_PHP_EXT_PDO_SQLITE_EXTERNAL),y)
			PHP_CONF_OPT += --with-pdo-sqlite=shared,$(STAGING_DIR)/usr
		else
			PHP_CONF_OPT += --with-pdo-sqlite=shared
		endif
		PHP_DEPENDENCIES += sqlite
	endif

	ifeq ($(BR2_PACKAGE_PHP_EXT_PDO_MYSQL),y)
		ifeq ($(BR2_PACKAGE_PHP_EXT_PDO_MYSQL_EXTERNAL),y)
			PHP_CONF_OPT += --with-pdo-mysql=shared,$(STAGING_DIR)/usr
		else
			PHP_CONF_OPT += --with-pdo-mysql=shared
		endif
		PHP_DEPENDENCIES += mysql
	endif
endif

ifeq (y,n)
PHP_CONF_OPT += --enable-pdo=shared \
	--with-sqlite3=shared,$(STAGING_DIR)/usr --with-pdo-sqlite=shared,$(STAGING_DIR)/usr \
	--with-mysql=shared,$(STAGING_DIR)/usr --with-pdo-mysql=shared,$(STAGING_DIR)/usr

PHP_DEPENDENCIES += mysql sqlite
endif

$(eval $(call AUTOTARGETS,package,php))

$(PHP_HOOK_POST_EXTRACT):
	sed -i '/unset.*ac_cv_func_dlopen/d' $(PHP_DIR)/configure
	touch $@
	
$(PHP_HOOK_POST_CONFIGURE):
ifeq ($(BR2_PACKAGE_PHP_EXT_PDO_MYSQL),y)
	# configure can't check for some C types (cross-compiling)
	touch $(PHP_DIR)/ext/mysqlnd/php_mysqlnd_config.h
endif
	# install-programs target sometimes fails (build/shtool mkdir -p concurrency issue?)
	mkdir -p $(TARGET_DIR)/usr/share/man/man1
	touch $@

$(PHP_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/bin/phpize
	rm -f $(TARGET_DIR)/usr/bin/php-config
	rm -rf $(TARGET_DIR)/usr/lib/build
	if [ ! -f $(TARGET_DIR)/etc/php.ini ]; then \
		$(INSTALL) -m 0755 $(BR2_PACKAGE_PHP_CONFIG) $(TARGET_DIR)/etc/php.ini; fi
	touch $@

$(PHP_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	rm -rf $(STAGING_DIR)/usr/include/php
	rm -rf $(STAGING_DIR)/usr/lib/php5
	rm -f $(STAGING_DIR)/usr/bin/php*
	rm -f $(STAGING_DIR)/usr/share/man/man1/php*.1
	rm -f $(TARGET_DIR)/etc/php.ini
	rm -f $(TARGET_DIR)/usr/bin/php*
	rm -f $(PHP_TARGET_INSTALL_TARGET) $(PHP_HOOK_POST_INSTALL)
