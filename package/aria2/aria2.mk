#############################################################
#
# aria2
#
#############################################################

# since 1.18.0 a C++11 (-std=c++0x) able compiler is needed, gcc-4.3.3 is not
#ARIA2_VERSION:=1.18.8 
ARIA2_VERSION:=1.17.1
ARIA2_SOURCE:=aria2-$(ARIA2_VERSION).tar.xz
ARIA2_SITE:=$(BR2_SOURCEFORGE_MIRROR)/project/aria2/stable/aria2-$(ARIA2_VERSION)

ARIA2_LIBTOOL_PATCH = NO
ARIA2_AUTORECONF = NO

ARIA2_CONF_OPT = --program-prefix="" 

$(eval $(call AUTOTARGETS,package,aria2))
