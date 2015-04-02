#############################################################
#
# python
#
#############################################################

PYTHON_VERSION=2.7.2
PYTHON_VERSION_MAJOR=2.7

PYTHON_SOURCE:=Python-$(PYTHON_VERSION).tar.bz2
PYTHON_SITE:=http://www.python.org/ftp/python/$(PYTHON_VERSION)

PYTHON_PIP_SITE=https://bootstrap.pypa.io
PYTHON_PIP_SOURCE=get-pip.py

PYTHON_DIR:=$(BUILD_DIR)/Python-$(PYTHON_VERSION)
PYTHON_CAT:=$(BZCAT)
PYTHON_BINARY:=python

PYTHON_TARGET_BINARY:=usr/bin/python
LIBPYTHON_BINARY:=usr/lib/libpython$(PYTHON_VERSION_MAJOR).so
PYTHON_SITE_PACKAGE_DIR=$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages

PYTHON_DEPS:=zlib-host

ifneq ($(BR2_INET_IPV6),y)
	DISABLE_IPV6= --disable-ipv6
else
	DISABLE_IPV6= --enable-ipv6
endif

BR2_PYTHON_DISABLED_MODULES:= 

ifeq ($(BR2_PACKAGE_PYTHON_READLINE),y)
PYTHON_DEPS += readline
else
BR2_PYTHON_DISABLED_MODULES += readline
endif

ifeq ($(BR2_PACKAGE_PYTHON_CURSES),y)
PYTHON_DEPS += ncurses
else
BR2_PYTHON_DISABLED_MODULES += _curses _curses_panel
endif

ifeq ($(BR2_PACKAGE_PYTHON_PYEXPAT),y)
PYTHON_DEPS += expat
PYTHON_SYS_EXPACT = --with-system-expat
else
BR2_PYTHON_DISABLED_MODULES += pyexpat
endif

ifeq ($(BR2_PACKAGE_PYTHON_GDBM),y)
PYTHON_DEPS += gdbm
else
BR2_PYTHON_DISABLED_MODULES += gdbm
endif

ifeq ($(BR2_PACKAGE_PYTHON_BSDDB),y)
PYTHON_DEPS += db
else
BR2_PYTHON_DISABLED_MODULES += _bsddb
endif

ifeq ($(BR2_PACKAGE_PYTHON_SQLITE3),y)
PYTHON_DEPS += sqlite
else
BR2_PYTHON_DISABLED_MODULES += _sqlite3
endif

ifeq ($(BR2_PACKAGE_PYTHON_BZIP2),y)
PYTHON_DEPS += bzip2
else
BR2_PYTHON_DISABLED_MODULES += bz2
endif

ifeq ($(BR2_PACKAGE_PYTHON_ZLIB),y)
PYTHON_DEPS += zlib
else
BR2_PYTHON_DISABLED_MODULES += zlib
endif

ifeq ($(BR2_PACKAGE_PYTHON_TKINTER),y)
PYTHON_DEPS += tcl
else
BR2_PYTHON_DISABLED_MODULES += _tkinter
endif

ifeq ($(BR2_PACKAGE_PYTHON_SSL),y)
PYTHON_DEPS += openssl
else
BR2_PYTHON_DISABLED_MODULES += _ssl
endif

ifneq ($(BR2_PACKAGE_PYTHON_NIS),y)
BR2_PYTHON_DISABLED_MODULES += nis
endif

ifneq ($(BR2_PACKAGE_PYTHON_CODECSCJK),y)
BR2_PYTHON_DISABLED_MODULES += _codecs_kr _codecs_jp _codecs_cn _codecs_tw _codecs_hk
endif

ifneq ($(BR2_PACKAGE_PYTHON_UNICODEDATA),y)
BR2_PYTHON_DISABLED_MODULES += unicodedata
endif

ifeq ($(BR2_PACKAGE_PYTHON_LOCALE),y)
PYTHON_DEPS += gettext
else
BR2_PYTHON_DISABLED_MODULES += _locale
endif

$(DL_DIR)/$(PYTHON_SOURCE):
	$(call DOWNLOAD,$(PYTHON_SITE),$(PYTHON_SOURCE))
	$(call DOWNLOAD,$(PYTHON_PIP_SITE),$(PYTHON_PIP_SOURCE))

$(PYTHON_DIR)/.unpacked: $(DL_DIR)/$(PYTHON_SOURCE)
	$(PYTHON_CAT) $(DL_DIR)/$(PYTHON_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(PYTHON_DIR)/.patched: $(PYTHON_DIR)/.unpacked
	toolchain/patch-kernel.sh $(PYTHON_DIR) package/python/ python-$(PYTHON_VERSION_MAJOR)-\*.patch
	touch $@

$(PYTHON_DIR)/.hostpython: $(PYTHON_DIR)/.patched
	$(call MESSAGE,"Building python for the host")
	(cd $(PYTHON_DIR); rm -rf config.cache; \
		./configure --prefix=/usr --libdir=/usr/lib --sysconfdir=/etc --disable-shared; \
		$(MAKE) python Parser/pgen; \
		mv python hostpython;  \
		mv Parser/pgen Parser/hostpgen; \
		PYTHON_MODULES_INCLUDE="$(HOST_DIR)/usr/include" \
		PYTHON_MODULES_LIB="$(HOST_DIR)/lib $(HOST_DIR)/usr/lib" \
		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \
		$(MAKE) all install DESTDIR=$(HOST_DIR); \
		$(MAKE) -i distclean \
	)
	# install pip (pip installs setuptools by default)
	LD_LIBRARY_PATH=$(HOST_DIR)/usr/lib/ $(HOST_DIR)/usr/bin/python $(DL_DIR)/$(PYTHON_PIP_SOURCE)
	touch $@

#		OPT="$(HOST_CFLAGS)" \
#		PYTHON_MODULES_INCLUDE="$(HOST_DIR)/usr/include" \
#		PYTHON_MODULES_LIB="$(HOST_DIR)/lib $(HOST_DIR)/usr/lib" \
#		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \

$(PYTHON_DIR)/.configured: $(PYTHON_DIR)/.hostpython
	$(call MESSAGE,"Configuring python for the target")
	(cd $(PYTHON_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		OPT="$(TARGET_CFLAGS)" \
		MACHDEP=linux2 \
		./configure \
		ac_sys_system=Linux \
		ac_sys_release=2 \
		ac_cv_buggy_getaddrinfo=no \
		--target=$(GNU_TARGET_NAME) \
		--host=$(GNU_TARGET_NAME) \
		--build=$(GNU_HOST_NAME) \
		--prefix=/usr \
		--libdir=/usr/lib \
		--sysconfdir=/etc \
		--enable-shared \
		$(PYTHON_SYS_EXPACT) \
		$(DISABLE_IPV6) \
		$(DISABLE_NLS) \
	)
	touch $@

$(PYTHON_DIR)/$(PYTHON_BINARY): $(PYTHON_DIR)/.configured
	$(call MESSAGE,"Building python for the target")
	$(MAKE) CC="$(TARGET_CC)" -C $(PYTHON_DIR) DESTDIR=$(TARGET_DIR) \
		PYTHON_MODULES_INCLUDE="$(STAGING_DIR)/usr/include" \
		PYTHON_MODULES_LIB="$(STAGING_DIR)/lib $(STAGING_DIR)/usr/lib" \
		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \
		HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen \
		CROSS_COMPILE=$(GNU_TARGET_NAME)- CROSS_COMPILE_TARGET=yes \
		HOSTARCH=$(GNU_TARGET_NAME) BUILDARCH=$(GNU_HOST_NAME) \
		BLDSHARED="$(TARGET_CC) -shared"
	touch -c $@

$(TARGET_DIR)/$(PYTHON_TARGET_BINARY): $(PYTHON_DIR)/$(PYTHON_BINARY)
	$(call MESSAGE,"Installing python on the target")
	rm -rf $(PYTHON_DIR)/Lib/test $(STAGING_DIR)/$(LIBPYTHON_BINARY).* $(TARGET_DIR)/$(LIBPYTHON_BINARY).*
	$(MAKE) CC=$(TARGET_CC) -C $(PYTHON_DIR) install DESTDIR=$(TARGET_DIR) \
		PYTHON_MODULES_INCLUDE=$(STAGING_DIR)/usr/include \
		PYTHON_MODULES_LIB="$(STAGING_DIR)/lib $(STAGING_DIR)/usr/lib" \
		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \
		PYTHONHOME=$(HOST_DIR)/usr \
		HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen \
		CROSS_COMPILE=$(GNU_TARGET_NAME)- CROSS_COMPILE_TARGET=yes \
		BLDSHARED="$(TARGET_CC) -shared"
	(cd $(TARGET_DIR)/usr/bin; ln -sf python$(PYTHON_VERSION_MAJOR) python )
	rm $(TARGET_DIR)/usr/bin/idle $(TARGET_DIR)/usr/bin/pydoc
	cp -dpr $(TARGET_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR) $(STAGING_DIR)/usr/include
	cp -dp $(TARGET_DIR)/$(LIBPYTHON_BINARY)* $(STAGING_DIR)/usr/lib
	mkdir -p $(STAGING_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)
	cp -dpr $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/config \
		$(STAGING_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/
	# python needs pyconfig.h and Makefile at runtime, save it! (buildroot remove /usr/include)
	cp $(TARGET_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)/pyconfig.h \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/config/Makefile \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)
	find $(TARGET_DIR)/usr/lib/ -name '*.pyo' -exec rm {} \;
ifeq ($(BR2_PACKAGE_PYTHON_PY_ONLY),y)
	find $(TARGET_DIR)/usr/lib/ -name '*.pyc' -exec rm {} \;
endif
ifeq ($(BR2_PACKAGE_PYTHON_PYC_ONLY),y)
	find $(TARGET_DIR)/usr/lib/ -name '*.py' -exec rm {} \;
endif
ifneq ($(BR2_PACKAGE_PYTHON_DEV),y)
	rm -f $(TARGET_DIR)/usr/bin/python*config
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/config
endif
ifneq ($(BR2_PACKAGE_PYTHON_BSDDB),y)
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/bsddb
endif
ifneq ($(BR2_PACKAGE_PYTHON_CURSES),y)
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/curses
endif
ifneq ($(BR2_PACKAGE_PYTHON_TKINTER),y)
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/lib-tk
endif
ifneq ($(BR2_PACKAGE_PYTHON_SQLITE3),y)
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/sqlite3
endif
	touch -c $@

#$(eval $(call AUTOTARGETS_HOST,package,python))

python: uclibc $(PYTHON_DEPS) $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)

python-extract: $(PYTHON_DIR)/.unpacked

python-patch: $(PYTHON_DIR)/.patched

python-host: $(PYTHON_DIR)/.hostpython

python-configure: $(PYTHON_DIR)/.configured

python-build: $(PYTHON_DIR)/$(PYTHON_BINARY)

python-install: $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)

python-clean:
	-$(MAKE) -C $(PYTHON_DIR) distclean
	rm -f $(PYTHON_DIR)/.configured $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)
	-rm -rf $(TARGET_DIR)/usr/lib/python* $(TARGET_DIR)/usr/include/python*
	-rm -f $(STAGING_DIR)/usr/lib/libpython$(PYTHON_VERSION_MAJOR).so

python-dirclean:
	rm -rf $(PYTHON_DIR)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_PYTHON),y)
TARGETS+=python
endif
