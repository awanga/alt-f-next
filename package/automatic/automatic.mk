#############################################################
#
# automatic
#
#############################################################

#AUTOMATIC_VERSION = 0.6.7
AUTOMATIC_VERSION = 0.7.2
AUTOMATIC_SOURCE = automatic-$(AUTOMATIC_VERSION)-src.tar.gz
AUTOMATIC_SITE = http://kylek.is-a-geek.org:31337/files/
AUTOMATIC_AUTORECONF = NO
AUTOMATIC_INSTALL_STAGING = NO
AUTOMATIC_INSTALL_TARGET = YES
AUTOMATIC_LIBTOOL_PATCH = NO

AUTOMATIC_DEPENDENCIES = host-pkgconfig uclibc libxml2 pcre libcurl libiconv openssl

$(eval $(call AUTOTARGETS,package,automatic))
