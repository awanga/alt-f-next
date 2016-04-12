#############################################################
#
# netperf
#
#############################################################

NETPERF_VERSION:=2.6.0
NETPERF_SOURCE:=netperf-$(NETPERF_VERSION).tar.gz
NETPERF_SITE:=ftp://ftp.netperf.org/netperf/archive

NETPERF_AUTORECONF:=NO
NETPERF_INSTALL_STAGING:=NO
NETPERF_INSTALL_TARGET:=YES

NETPERF_CONF_ENV:=ac_cv_func_setpgrp_void=yes
NETPERF_CONF_OPT:=--program-prefix=""

NETPERF_DEPENDENCIES:=uclibc

$(eval $(call AUTOTARGETS,package,netperf))
