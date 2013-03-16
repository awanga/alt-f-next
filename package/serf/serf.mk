#############################################################
#
# serf
#
#############################################################

SERF_VERSION = 1.1.1
SERF_SITE = http://serf.googlecode.com/files
SERF_SOURCE = serf-$(SERF_VERSION).tar.bz2
SERF_INSTALL_STAGING = YES
SERF_LIBTOOL_PATCH = NO

SERF_CONF_OPT = \
	--with-apr=$(APR_DIR)

$(eval $(call AUTOTARGETS,package,serf))
