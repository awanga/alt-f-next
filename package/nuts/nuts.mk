#############################################################
#
# nuts
#
#############################################################

NUTS_VERSION = 2.6.1
NUTS_SOURCE = nut-$(NUTS_VERSION).tar.gz
NUTS_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/nut
NUTS_AUTORECONF = NO
NUTS_INSTALL_STAGING = NO
NUTS_INSTALL_TARGET = YES
NUTS_LIBTOOL_PATCH = NO
	
NUTS_DEPENDENCIES = uclibc libusb netsnmp openssl libgd
NUTS_CONF_ENV = LIBS=-lm
NUTS_CONF_OPT = --with-user=ups --with-group=nut \
	--with-snmp-libs=-lnetsnmp --program-prefix="" 
#	--with-cgi --with-htmlpath=/usr/www --with-cgipath=/usr/www/cgi-bi

$(eval $(call AUTOTARGETS,package,nuts))
	
$(NUTS_HOOK_POST_INSTALL):
	(cd $(TARGET_DIR)/etc; \
	for i in nut.conf ups.conf upsd.conf upsd.users upsmon.conf upssched.conf; do \
	mv $$i.sample $$i; \
	done; \
	)
	touch $@
