#############################################################
#
# polipo
#
#############################################################

POLIPO_VERSION = 1.0.4.1
POLIPO_SOURCE = polipo-$(POLIPO_VERSION).tar.gz
POLIPO_SITE = http://freehaven.net/~chrisd/polipo
POLIPO_AUTORECONF = NO 
POLIPO_INSTALL_STAGING = NO
POLIPO_INSTALL_TARGET = YES
POLIPO_LIBTOOL_PATCH = NO

POLIPO_MAKE_ENV = CC="$(TARGET_CC)" CDEBUGFLAGS="$(TARGET_CFLAGS)" PREFIX=/usr 

POLIPO_INSTALL_TARGET_OPT = TARGET=$(TARGET_DIR) install.binary

$(eval $(call AUTOTARGETS,package,polipo))

$(POLIPO_HOOK_POST_EXTRACT):
	echo '#!/bin/sh' > $(POLIPO_DIR)/configure
	chmod +x $(POLIPO_DIR)/configure
	sed -i -e '/^CDEBUGFLAGS.*/d' \
		-e '/^PREFIX.*/d' \
		-e 's|^DISK_CACHE_ROOT.*|DISK_CACHE_ROOT = /var/spool/polipo|' /$(POLIPO_DIR)/Makefile
	touch $@

$(POLIPO_HOOK_POST_INSTALL):
	mkdir -p $(TARGET_DIR)/etc/polipo
	cp $(POLIPO_DIR)/config.sample $(TARGET_DIR)/etc/polipo/config
	sed -i -e 's/#.*proxyAddress.*=.*"0.0.0.0"/proxyAddress = "0.0.0.0"/' \
		-e '/### Memory/i \
daemonise = true \
pidFile = /var/run/polipo.pid \
logFile = /var/log/polipo.log\n' $(TARGET_DIR)/etc/polipo/config
	touch $@

