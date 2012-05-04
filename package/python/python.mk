#############################################################
#
# python
#
#############################################################
#PYTHON_VERSION=2.4.5
#PYTHON_VERSION_MAJOR=2.4
PYTHON_VERSION=2.7.2
PYTHON_VERSION_MAJOR=2.7

PYTHON_SOURCE:=Python-$(PYTHON_VERSION).tar.bz2
PYTHON_SITE:=http://python.org/ftp/python/$(PYTHON_VERSION)
PYTHON_DIR:=$(BUILD_DIR)/Python-$(PYTHON_VERSION)
PYTHON_CAT:=$(BZCAT)
PYTHON_BINARY:=python
PYTHON_TARGET_BINARY:=usr/bin/python
PYTHON_DEPS:=
PYTHON_SITE_PACKAGE_DIR=$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/site-packages

ifneq ($(BR2_INET_IPV6),y)
	DISABLE_IPV6= --disable-ipv6
else
	DISABLE_IPV6= --enable-ipv6
endif

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
BR2_PYTHON_DISABLED_MODULES += bsddb
endif

ifeq ($(BR2_PACKAGE_PYTHON_SQLITE3),y)
PYTHON_DEPS += sqlite
else
BR2_PYTHON_DISABLED_MODULES += _sqlite3
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

$(DL_DIR)/$(PYTHON_SOURCE):
	 $(call DOWNLOAD,$(PYTHON_SITE),$(PYTHON_SOURCE))

$(PYTHON_DIR)/.unpacked: $(DL_DIR)/$(PYTHON_SOURCE)
	$(PYTHON_CAT) $(DL_DIR)/$(PYTHON_SOURCE) | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	touch $@

$(PYTHON_DIR)/.patched: $(PYTHON_DIR)/.unpacked
	toolchain/patch-kernel.sh $(PYTHON_DIR) package/python/ python-$(PYTHON_VERSION_MAJOR)-\*.patch
	touch $@

$(PYTHON_DIR)/.hostpython: $(PYTHON_DIR)/.patched
	(cd $(PYTHON_DIR); rm -rf config.cache; \
		CC="$(HOSTCC)" OPT="-O2" \
		./configure \
		$(DISABLE_NLS) && \
		$(MAKE) python Parser/pgen && \
		mv python hostpython && \
		mv Parser/pgen Parser/hostpgen && \
		$(MAKE) distclean \
	) && \
	touch $@

$(PYTHON_DIR)/.configured: $(PYTHON_DIR)/.hostpython
	(cd $(PYTHON_DIR); rm -rf config.cache; \
		$(TARGET_CONFIGURE_OPTS) \
		$(TARGET_CONFIGURE_ARGS) \
		OPT="$(TARGET_CFLAGS)" \
		MACHDEP=linux2 \
		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \
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
		$(DISABLE_IPV6) \
		$(DISABLE_NLS) \
	)
	touch $@

$(PYTHON_DIR)/$(PYTHON_BINARY): $(PYTHON_DIR)/.configured
	$(MAKE) CC=$(TARGET_CC) -C $(PYTHON_DIR) DESTDIR=$(TARGET_DIR) \
		PYTHON_MODULES_INCLUDE=$(STAGING_DIR)/usr/include \
		PYTHON_MODULES_LIB="$(STAGING_DIR)/lib $(STAGING_DIR)/usr/lib" \
		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \
		HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen \
		CROSS_COMPILE=arm-linux- CROSS_COMPILE_TARGET=yes \
		HOSTARCH=arm-linux BUILDARCH=x86_64-pc-linux-gnu \
		BLDSHARED="arm-linux-gcc -shared"

python-install: $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)

$(TARGET_DIR)/$(PYTHON_TARGET_BINARY): $(PYTHON_DIR)/$(PYTHON_BINARY)
	rm -rf $(PYTHON_DIR)/Lib/test
	# LD_LIBRARY_PATH=$(STAGING_DIR)/lib
	$(MAKE) CC=$(TARGET_CC) -C $(PYTHON_DIR) install \
		DESTDIR=$(TARGET_DIR) CROSS_COMPILE=yes \
		PYTHON_MODULES_INCLUDE=$(STAGING_DIR)/usr/include \
		PYTHON_MODULES_LIB="$(STAGING_DIR)/lib $(STAGING_DIR)/usr/lib" \
		PYTHON_DISABLE_MODULES="$(BR2_PYTHON_DISABLED_MODULES)" \
		HOSTPYTHON=./hostpython HOSTPGEN=./Parser/hostpgen
	rm $(TARGET_DIR)/usr/bin/python
	( cd $(TARGET_DIR)/usr/bin; ln -s python$(PYTHON_VERSION_MAJOR) python )
	chmod u+w $(TARGET_DIR)/usr/lib/libpython$(PYTHON_VERSION_MAJOR).so
	$(STRIPCMD) $(TARGET_DIR)/usr/lib/libpython$(PYTHON_VERSION_MAJOR).so
	$(STRIPCMD) $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/lib-dynload/*.so
	rm $(TARGET_DIR)/usr/bin/idle $(TARGET_DIR)/usr/bin/pydoc
	rm -rf $(TARGET_DIR)/share/locale $(TARGET_DIR)/usr/info \
		$(TARGET_DIR)/usr/man $(TARGET_DIR)/usr/share/doc \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/test
	cp -dpr $(TARGET_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR) $(STAGING_DIR)/usr/include/
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
	#rm -rf $(TARGET_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)
	#find $(TARGET_DIR)/usr/lib/ -name '*.py' -exec rm {} \;
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

python: uclibc $(PYTHON_DEPS) $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)

python-host: $(PYTHON_DIR)/.hostpython

python-configure: $(PYTHON_DIR)/.configured

python-build: $(PYTHON_DIR)/$(PYTHON_BINARY)

python-clean:
	-$(MAKE) -C $(PYTHON_DIR) distclean
	rm -f $(PYTHON_DIR)/.configured $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)
	-rm -rf $(TARGET_DIR)/usr/lib/python* $(TARGET_DIR)/usr/include/python*
	-rm -f $(STAGING_DIR)/usr/lib/libpython$(PYTHON_VERSION_MAJOR).so

python-dirclean:
	rm -rf $(PYTHON_DIR)

####  LIBPYTHON

LIBPYTHON_BINARY:=libpython$(PYTHON_VERSION_MAJOR).so

libpython:	python $(TARGET_DIR)/usr/lib/$(LIBPYTHON_BINARY)

$(STAGING_DIR)/usr/lib/libpython$(PYTHON_VERSION_MAJOR).so: $(TARGET_DIR)/$(PYTHON_TARGET_BINARY)
		cp -dpr $(PYTHON_DIR)/$(LIBPYTHON_BINARY).* $(STAGING_DIR)/usr/lib
		(\
		cd $(STAGING_DIR)/usr/lib ; \
		rm -f $(LIBPYTHON_BINARY) ; \
		ln -s `basename  \`ls libpython*.so.*\`` $(LIBPYTHON_BINARY) \
		)

$(TARGET_DIR)/usr/lib/$(LIBPYTHON_BINARY): $(STAGING_DIR)/usr/lib/$(LIBPYTHON_BINARY)
		cp -dpr $(STAGING_DIR)/usr/lib/$(LIBPYTHON_BINARY).* $(TARGET_DIR)/usr/lib
		(\
		cd $(TARGET_DIR)/usr/lib ; \
		rm -f $(LIBPYTHON_BINARY) ; \
		ln -s `basename  \`ls libpython*.so.*\`` $(LIBPYTHON_BINARY) \
		)

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_PYTHON),y)
TARGETS+=python
endif
