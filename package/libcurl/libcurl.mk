#############################################################
#
# libcurl
#
#############################################################

LIBCURL_VERSION = 7.22.0
LIBCURL_SOURCE = curl-$(LIBCURL_VERSION).tar.bz2
LIBCURL_SITE = http://curl.haxx.se/download/

LIBCURL_INSTALL_STAGING = YES
LIBCURL_LIBTOOL_PATCH = NO
LIBCURL_CONF_OPT = --disable-verbose --disable-manual --enable-hidden-symbols

ifeq ($(BR2_PACKAGE_OPENSSL),y)
LIBCURL_DEPENDENCIES += openssl
LIBCURL_CONF_ENV += ac_cv_lib_crypto_CRYPTO_lock=yes
# configure adds the cross openssl dir to LD_LIBRARY_PATH which screws up
# native stuff during the rest of configure when target == host.
# Fix it by setting LD_LIBRARY_PATH to something sensible so those libs
# are found first.
LIBCURL_CONF_ENV += LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:/lib:/usr/lib
LIBCURL_CONF_OPT += --with-ssl=$(STAGING_DIR)/usr --with-random=/dev/urandom --with-ca-bundle=/etc/ssl/ca-bundle.crt
else
LIBCURL_CONF_OPT += --without-ssl
endif

ifeq ($(BR2_INET_IPV6),y)
LIBCURL_CONF_OPT += --enable-ipv6
else
LIBCURL_CONF_OPT += $(DISABLE_IPV6)
endif

$(eval $(call AUTOTARGETS,package,libcurl))

$(LIBCURL_HOOK_POST_INSTALL):
	rm -f $(STAGING_DIR)/usr/bin/curl
	rm -f $(TARGET_DIR)/usr/bin/curl-config \
	       $(if $(BR2_PACKAGE_CURL),,$(TARGET_DIR)/usr/bin/curl)
	touch $@

curl: libcurl
curl-clean: libcurl-clean
curl-dirclean: libcurl-dirclean
curl-source: libcurl-source
