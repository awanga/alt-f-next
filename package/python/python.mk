#############################################################
#
# python
#
############################################################

PYTHON_VERSION=2.7.14
PYTHON_VERSION_MAJOR=2.7

PYTHON_SOURCE:=Python-$(PYTHON_VERSION).tar.xz
PYTHON_SITE:=http://www.python.org/ftp/python/$(PYTHON_VERSION)

PYTHON_INSTALL_STAGING = YES
PYTHON_INSTALL_TARGET = YES
PYTHON_AUTORECONF = YES
PYTHON_LIBTOOL_PATCH = NO

PYTHON_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

# host. patches are not applied to the host build
PYTHON_HOST_DEPENDENCIES = expat-host zlib-host openssl-host

PYTHON_HOST_CONF_ENV += \
	ac_cv_prog_HAS_HG=/bin/false \
	ac_cv_prog_SVNVERSION=/bin/false

PYTHON_HOST_CONF_OPT += --without-cxx-main --with-system-expat

# target
PYTHON_CONF_ENV += \
	ac_cv_have_long_long_format=yes \
	ac_cv_file__dev_ptmx=yes \
	ac_cv_file__dev_ptc=yes \
	ac_cv_working_tzset=yes \
	ac_cv_prog_HAS_HG=/bin/false \
	ac_cv_prog_SVNVERSION=/bin/false

ifeq ($(BR2_ENDIAN),"LITTLE")
PYTHON_CONF_ENV += ac_cv_little_endian_double=yes
else
PYTHON_CONF_ENV += ac_cv_big_endian_double=yes
endif

PYTHON_CONF_ENV += LIBS=-lintl

PYTHON_CONF_OPT = --disable-nis --disable-ossaudiodev
#PYTHON_CONF_OPT += --with-pydebug

PYTHON_CONF_OPT += \
	--enable-shared \
	--without-cxx-main \
	--without-doc-strings \
	--disable-pydoc \
	--disable-pyo-build \
	--disable-pyc-build \
	--disable-test-modules

PYTHON_DEPENDENCIES = python-host

ifeq ($(BR2_PACKAGE_PYTHON_READLINE),y)
PYTHON_DEPENDENCIES += readline
else
PYTHON_CONF_OPT += --disable-readline
endif

ifeq ($(BR2_PACKAGE_PYTHON_CURSES),y)
PYTHON_DEPENDENCIES += ncurses
else
PYTHON_CONF_OPT += --disable-curses
endif

ifeq ($(BR2_PACKAGE_PYTHON_LIBFFI),y)
PYTHON_DEPENDENCIES += libffi
PYTHON_CONF_OPT += --with-system-ffi
endif

ifeq ($(BR2_PACKAGE_PYTHON_PYEXPAT),y)
PYTHON_DEPENDENCIES += expat
PYTHON_CONF_OPT += --with-expat=system
else
PYTHON_CONF_OPT += --with-expat=none
endif

ifeq ($(BR2_PACKAGE_PYTHON_GDBM),y)
PYTHON_DEPENDENCIES += gdbm
else
PYTHON_CONF_OPT += --disable-gdbm 
endif

ifeq ($(BR2_PACKAGE_PYTHON_BSDDB),y)
PYTHON_DEPENDENCIES += db
else
PYTHON_CONF_OPT += --disable-bsddb
endif

ifeq ($(BR2_PACKAGE_PYTHON_SQLITE3),y)
PYTHON_DEPENDENCIES += sqlite
else
PYTHON_CONF_OPT += --disable-sqlite3
endif

ifeq ($(BR2_PACKAGE_PYTHON_BZIP2),y)
PYTHON_DEPENDENCIES += bzip2
else
PYTHON_CONF_OPT += --disable-bz2
endif

ifeq ($(BR2_PACKAGE_PYTHON_ZLIB),y)
PYTHON_DEPENDENCIES += zlib
else
PYTHON_CONF_OPT += --disable-zlib
endif

ifeq ($(BR2_PACKAGE_PYTHON_TKINTER),y)
PYTHON_DEPENDENCIES += tcl
else
PYTHON_CONF_OPT += --disable-tk
endif

ifeq ($(BR2_PACKAGE_PYTHON_SSL),y)
PYTHON_DEPENDENCIES += openssl
else
PYTHON_CONF_OPT += --disable-ssl
endif

ifeq ($(BR2_PACKAGE_PYTHON_LOCALE),y)
PYTHON_DEPENDENCIES += gettext
endif

ifneq ($(BR2_PACKAGE_PYTHON_CODECSCJK),y)
PYTHON_CONF_OPT += --disable-codecs-cjk
endif

ifeq ($(BR2_PACKAGE_PYTHON_UNICODEDATA),y)
PYTHON_CONF_OPT += --enable-unicodedata 
endif

$(eval $(call AUTOTARGETS,package,python))
$(eval $(call AUTOTARGETS_HOST,package,python))

# host, can't find openssl...
$(PYTHON_HOST_HOOK_POST_EXTRACT):
	$(SED) 's|/usr/contrib/ssl|$(HOST_DIR)/usr|' $(PYTHON_HOST_DIR)/setup.py
	touch $@

# target
$(PYTHON_HOOK_POST_INSTALL):
	ln -sf python2 $(TARGET_DIR)/usr/bin/python
	# pip for the target. Remove if already installed in host_dir
	if test $$(which pip) = "$(HOST_DIR)/usr/bin/pip"; then pip uninstall setuptools pip; fi
	tf=$$(mktemp -d); \
	HOME=. python -m ensurepip --root=$$tf --user; \
	find $$tf/.local -name \*.pyc -delete; \
	sed -i '1s|#!.*/usr/|#!/usr/|' $$tf/.local/bin/*; \
	cp -a $$tf/.local/* $(TARGET_DIR)/usr/; \
	rm -rf $$tf
	# pip for the host, can't be done before 
	python -m ensurepip
	#adjust paths to compile extentions, and install the dev-headers-bundle package on target
	for i in config/Makefile _sysconfigdata.py sysconfig.py \
		sysconfigdata/_sysconfigdata.py lib-dynload/sysconfigdata/_sysconfigdata.py; do \
		$(SED) 's|$(STAGING_DIR)||g' \
			-e 's|--sysroot=/||g' \
			-e 's|-isysroot||g' \
			-e 's|arm-linux-uclibcgnueabi-||g' $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/$$i; \
	done
	mv $(TARGET_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)/pyconfig.h \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/config/Makefile \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/config
	rm -f $(TARGET_DIR)/usr/bin/python-config \
		$(TARGET_DIR)/usr/bin/python2-config \
		$(TARGET_DIR)/usr/bin/python$(PYTHON_VERSION_MAJOR)-config \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/lib-dynload/sysconfigdata.pyc \
		$(TARGET_DIR)/usr/lib/python$(PYTHON_VERSION_MAJOR)/lib-dynload/sysconfigdata/_sysconfigdata.pyc
	touch $@
