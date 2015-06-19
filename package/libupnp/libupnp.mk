#############################################################
#
# libupnp
#
#############################################################

LIBUPNP_VERSION:=1.6.6
LIBUPNP_SOURCE:=libupnp-$(LIBUPNP_VERSION).tar.bz2
LIBUPNP_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/pupnp/pupnp/libUPnP%20$(LIBUPNP_VERSION)

#http://heanet.dl.sourceforge.net/project/pupnp/pupnp/libUPnP%201.6.19/libupnp-1.6.19.tar.bz2

LIBUPNP_CONF_ENV = ac_cv_lib_compat_ftime=no

LIBUPNP_INSTALL_STAGING:=YES

$(eval $(call AUTOTARGETS,package,libupnp))
