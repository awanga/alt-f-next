#############################################################
#
# rpcbind
#
#############################################################

RPCBIND_VERSION = 0.2.0
RPCBIND_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/project/rpcbind/rpcbind/$(RPCBIND_VERSION)
RPCBIND_SOURCE = rpcbind-$(RPCBIND_VERSION).tar.bz2

RPCBIND_AUTORECONF = NO
RPCBIND_INSTALL_STAGING = YES
RPCBIND_INSTALL_TARGET = YES
RPCBIND_LIBTOOL_PATCH = NO

$(eval $(call AUTOTARGETS,package,rpcbind))

