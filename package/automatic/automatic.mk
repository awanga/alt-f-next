#############################################################
#
# automatic
#
#############################################################

#AUTOMATIC_VERSION = 0.7.2
#AUTOMATIC_SOURCE = automatic-$(AUTOMATIC_VERSION)-src.tar.gz
#AUTOMATIC_SITE = http://kylek.is-a-geek.org:31337/files/

# moved to github: https://github.com/1100101/Automatic/archive/v0.8.3.tar.gz
AUTOMATIC_VERSION = 0.8.3
AUTOMATIC_SOURCE = automatic-$(AUTOMATIC_VERSION).tar.gz
AUTOMATIC_SITE = https://github.com/1100101/Automatic/archive

AUTOMATIC_AUTORECONF = NO
AUTOMATIC_INSTALL_STAGING = NO
AUTOMATIC_INSTALL_TARGET = YES
AUTOMATIC_LIBTOOL_PATCH = NO

AUTOMATIC_DEPENDENCIES = host-pkgconfig uclibc libxml2 pcre libcurl libiconv openssl

AUTOMATIC_CONF_ENV = LIBXML_CFLAGS="-I$(STAGING_DIR)/usr/include/libxml2" \
	LIBXML_LIBS="-L$(STAGING_DIR)/usr/lib -lxml2"

$(eval $(call AUTOTARGETS,package,automatic))

$(AUTOMATIC_TARGET_SOURCE):
	$(call DOWNLOAD,$(AUTOMATIC_SITE),v$(AUTOMATIC_VERSION).tar.gz)
	(cd $(DL_DIR); ln -sf v$(AUTOMATIC_VERSION).tar.gz automatic-$(AUTOMATIC_VERSION).tar.gz )
	mkdir -p $(BUILD_DIR)/automatic-$(AUTOMATIC_VERSION)
	touch $@

$(AUTOMATIC_HOOK_POST_EXTRACT):
	(cd $(AUTOMATIC_DIR); ./autogen.sh)
	touch $@

$(AUTOMATIC_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/etc/automatic.conf-sample
	touch $@