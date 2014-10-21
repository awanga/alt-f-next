#############################################################
#
# cppunit
#
#############################################################

CPPUNIT_VERSION = 1.13.2
CPPUNIT_SOURCE = cppunit-$(CPPUNIT_VERSION).tar.gz
CPPUNIT_SITE = http://dev-www.libreoffice.org/src/

CPPUNIT_LIBTOOL_PATCH = NO
CPPUNIT_INSTALL_STAGING = YES
CPPUNIT_INSTALL_TARGET = NO

$(eval $(call AUTOTARGETS,package,cppunit))
