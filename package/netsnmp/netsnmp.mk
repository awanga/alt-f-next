#############################################################
#
# netsnmp
#
############################################################

NETSNMP_VERSION:=5.7.3
NETSNMP_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/net-snmp/net-snmp/$(NETSNMP_VERSION)
NETSNMP_DIR:=$(BUILD_DIR)/net-snmp-$(NETSNMP_VERSION)
NETSNMP_SOURCE:=net-snmp-$(NETSNMP_VERSION).tar.gz
NETSNMP_INSTALL_STAGING = YES
NETSNMP_LIBTOOL_PATCH = NO
NETSNMP_MAKE = $(MAKE1)

NETSNMP_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) installprogs installlibs installsubdirs
NETSNMP_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) installprogs installlibs installsubdirs installheaders

NETSNMP_WO_TRANSPORT:=
ifneq ($(BR2_INET_IPX),y)
NETSNMP_WO_TRANSPORT+= IPX
endif
ifneq ($(BR2_INET_IPV6),y)
NETSNMP_WO_TRANSPORT+= UDPIPv6 TCPIPv6
endif

ifeq ($(BR2_ENDIAN),"BIG")
NETSNMP_ENDIAN=big
else
NETSNMP_ENDIAN=little
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
NETSNMP_CONFIGURE_OPENSSL:=--with-openssl=$(STAGING_DIR)/usr
NETSNMP_DEPENDENCIES = openssl
else
NETSNMP_CONFIGURE_OPENSSL:=--without-openssl
endif

NETSNMP_CONF_OPT = $(NETSNMP_CONFIGURE_OPENSSL) \
	--with-out-transports="$(NETSNMP_WO_TRANSPORT)"  \
	--with-out-mib-modules=" " \
	--disable-embedded-perl --disable-perl-cc-checks --without-perl-modules \
	--without-kmem-usage --without-rsaref  --with-defaults \
	--with-sys-location="Unknown" --with-sys-contact="root" \
	--with-endianness=$(NETSNMP_ENDIAN) \
	--with-persistent-directory=/var/lib/snmp \
	--enable-ucd-snmp-compatibility \
	--enable-shared --disable-static \
	--without-rpm --disable-manuals 

NETSNMP_CONF_ENV = ac_cv_NETSNMP_CAN_USE_SYSCTL=no

$(eval $(call AUTOTARGETS,package,netsnmp))

$(NETSNMP_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/man $(TARGET_DIR)/usr/share/doc $(TARGET_DIR)/usr/share/info
	$(SED) "s|^prefix=.*|prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^exec_prefix=.*|exec_prefix=\'$(STAGING_DIR)/usr\'|g" \
		-e "s|^libdir=.*|libdir=\'$(STAGING_DIR)/usr/lib\'|g" \
		$(STAGING_DIR)/usr/bin/net-snmp-config
	# Copy the .conf files.
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/EXAMPLE.conf $(TARGET_DIR)/etc/snmp/EXAMPLE.conf
	# Install the "broken" headers
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/struct.h $(STAGING_DIR)/usr/include/net-snmp/agent/struct.h
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/util_funcs.h $(STAGING_DIR)/usr/include/net-snmp/util_funcs.h
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/mibincl.h $(STAGING_DIR)/usr/include/net-snmp/library/mibincl.h
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/header_complex.h $(STAGING_DIR)/usr/include/net-snmp/agent/header_complex.h
	touch $@
