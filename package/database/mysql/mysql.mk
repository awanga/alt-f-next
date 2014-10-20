################################################################################
#
# mysql
#
################################################################################

# later versions (5.5, 5.6) uses cmake
MYSQL_VERSION_MAJOR = 5.1
MYSQL_VERSION = 5.1.73
MYSQL_SOURCE = mysql-$(MYSQL_VERSION).tar.gz
MYSQL_SITE = http://downloads.skysql.com/archives/mysql-$(MYSQL_VERSION_MAJOR)

MYSQL_INSTALL_STAGING = YES
MYSQL_DEPENDENCIES = readline ncurses
MYSQL_AUTORECONF = YES
MYSQL_LIBTOOL_PATCH = NO

MYSQL_CONF_ENV = \
	ac_cv_sys_restartable_syscalls=yes \
	ac_cv_path_PS=/bin/ps \
	ac_cv_FIND_PROC="/bin/ps p \$\$PID | grep -v grep | grep mysqld > /dev/null" \
	ac_cv_have_decl_HAVE_IB_ATOMIC_PTHREAD_T_GCC=yes \
	ac_cv_have_decl_HAVE_IB_ATOMIC_PTHREAD_T_SOLARIS=no \
	ac_cv_have_decl_HAVE_IB_GCC_ATOMIC_BUILTINS=yes \
	mysql_cv_new_rl_interface=yes \
	ac_cv_func_isnan=yes

MYSQL_CONF_OPT = \
	--with-unix-socket-path=/var/run/mysql/mysql.sock \
	--localstatedir=/var/lib/mysql \
	--libexecdir=/usr/sbin \
	--program-prefix="" \
	--without-ndb-binlog \
	--without-docs \
	--without-man \
	--without-libedit \
	--without-readline \
	--without-bench \
	--enable-thread-safe-client \
	--disable-mysql-maintainer-mode \
	--with-charset=utf8

ifeq ($(BR2_PACKAGE_OPENSSL),y)
MYSQL_DEPENDENCIES += openssl
MYSQL_CONF_OPT += -with-ssl=$(STAGING_DIR)/usr
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
MYSQL_DEPENDENCIES += zlib
MYSQL_CONF_OPT += --with-zlib-dir=$(STAGING_DIR)/usr
endif

ifeq ($(BR2_PACKAGE_MYSQL_SERVER),y)

MYSQL_DEPENDENCIES += mysql-host bison-host
MYSQL_HOST_DEPENDENCIES = zlib-host

MYSQL_HOST_CONF_OPT = \
	--with-embedded-server \
	--disable-mysql-maintainer-mode

MYSQL_CONF_OPT += \
	--with-atomic-ops=up \
	--with-embedded-server \
	--without-query-cache

# Debugging is only available for the server, so no need for
# this if-block outside of the server if-block
ifeq ($(BR2_ENABLE_DEBUG),y)
MYSQL_CONF_OPT += --with-debug=full
else
MYSQL_CONF_OPT += --without-debug
endif

$(eval $(call AUTOTARGETS,package/database,mysql))
$(eval $(call AUTOTARGETS_HOST,package/database,mysql))

$(MYSQL_HOST_BUILD):
	$(MAKE) -C $(@D)/include my_config.h
	$(MAKE) -C $(@D)/mysys libmysys.a
	$(MAKE) -C $(@D)/strings libmystrings.a
	$(MAKE) -C $(@D)/vio libvio.a
	$(MAKE) -C $(@D)/dbug libdbug.a
	$(MAKE) -C $(@D)/regex libregex.a
	$(MAKE) -C $(@D)/sql gen_lex_hash
	touch $@

$(MYSQL_HOST_INSTALL):
	$(INSTALL) -m 0755  $(@D)/sql/gen_lex_hash  $(HOST_DIR)/usr/bin/
	touch $@

else

MYSQL_CONF_OPT += --without-server

endif

$(MYSQL_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/mysql-test $(TARGET_DIR)/usr/sql-bench
	touch $@
