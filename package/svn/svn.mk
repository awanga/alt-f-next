#############################################################
#
# svn
#
#############################################################

SVN_VERSION = 1.7.7
SVN_SITE = http://archive.apache.org/dist/subversion
SVN_SOURCE = subversion-$(SVN_VERSION).tar.bz2

SVN_AUTORECONF = NO
SVN_INSTALL_STAGING = NO
SVN_INSTALL_TARGET = YES
SVN_LIBTOOL_PATCH = NO
SVN_DEPENDENCIES = uclibc apr apr-util file db sqlite zlib openssl neon

# there are non-handled dependencies, don't run paralel make
SVN_MAKE_OPT = -j1

SVN_CONF_OPT = --with-apr=$(STAGING_DIR)/usr/bin/apr-1-config \
	--with-apr-util=$(STAGING_DIR)/usr/bin/apu-1-config \
	--disable-static

SVN_INSTALL_TARGET_OPT = $(SVN_MAKE_OPT) DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,svn))
