#############################################################
#
# alsa-lib
#
#############################################################

ALSA_LIB_VERSION = 1.0.26
ALSA_LIB_SOURCE = alsa-lib-$(ALSA_LIB_VERSION).tar.bz2
ALSA_LIB_SITE = ftp://ftp.alsa-project.org/pub/lib
ALSA_LIB_LIBTOOL_PATCH = NO
ALSA_LIB_INSTALL_STAGING = YES
ALSA_LIB_INSTALL_TARGET = YES

ALSA_LIB_CFLAGS=$(TARGET_CFLAGS)

ALSA_LIB_DEPENDENCIES = uclibc

ALSA_LIB_CONF_OPT = --enable-shared \
		    --disable-static \
			--disable-alisp --disable-python --disable-aload \
			--program-prefix="" --without-versioned

ifeq ($(BR2_ENABLE_DEBUG),y)
# install-exec doesn't install the config files
ALSA_LIB_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
ALSA_LIB_CONF_OPT += --enable-debug
endif

ifeq ($(BR2_avr32),y)
ALSA_LIB_CFLAGS+=-DAVR32_INLINE_BUG
endif

#ifeq ($(BR2_PACKAGE_ALSA_LIB_PYTHON),y)
#ALSA_LIB_CONF_OPT += --with-pythonlibs=-lpython$(PYTHON_VERSION_MAJOR)
#ALSA_LIB_CFLAGS+=-I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)
#ALSA_LIB_DEPENDENCIES += libpython
#else
#ALSA_LIB_CONF_OPT += --disable-python
#endif

ifeq ($(BR2_SOFT_FLOAT),y)
ALSA_LIB_CONF_OPT += --with-softfloat
endif

ALSA_LIB_CONF_ENV = CFLAGS="$(ALSA_LIB_CFLAGS)" \
		    LDFLAGS="$(TARGET_LDFLAGS) -lm"

$(eval $(call AUTOTARGETS,package/multimedia,alsa-lib))

$(ALSA_LIB_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/aclocal
	touch $@