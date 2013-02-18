#############################################################
#
# davfs2
#
#############################################################

DAVFS2_VERSION = 1.4.7
DAVFS2_SITE = http://download.savannah.gnu.org/releases/davfs2

DAVFS2_SOURCE = davfs2-$(DAVFS2_VERSION).tar.gz
DAVFS2_AUTORECONF = NO
DAVFS2_LIBTOOL_PATCH = YES
DAVFS2_INSTALL_STAGING = NO
DAVFS2_INSTALL_TARGET = YES
DAVFS2_DEPENDENCIES = uclibc neon libiconv

#DAVFS2_CONF_OPT = --with-libiconv-prefix=$(STAGING_DIR)/usr
#	--with-neon=$(STAGING_DIR)/usr/lib

DAVFS2_CONF_ENV = LIBS=-liconv

$(eval $(call AUTOTARGETS,package,davfs2))

$(DAVFS2_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/davfs2
	touch $@
