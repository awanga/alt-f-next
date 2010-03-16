#############################################################
#
# MediaTomb
#
#############################################################
MEDIATOMB_VERSION = 0.11.0
MEDIATOMB_SOURCE = mediatomb-$(MEDIATOMB_VERSION).tar.gz
MEDIATOMB_SITE = http://downloads.sourceforge.net/project/mediatomb/MediaTomb/0.11.0/
MEDIATOMB_AUTORECONF = NO
MEDIATOMB_INSTALL_STAGING = NO
MEDIATOMB_INSTALL_TARGET = YES
MEDIATOMB_LIBTOOL_PATCH = NO
MEDIATOMB_DEPENDENCIES = uclibc sqlite
#MEDIATOMB_CONF_OPT = 

$(eval $(call AUTOTARGETS,package,mediatomb))

