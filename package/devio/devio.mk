#############################################################
#
# devio for the host
#
#############################################################

DEVIO_VERSION = 1.2
DEVIO_SITE = $(BR2_SOURCEFORGE_MIRROR)/devio
DEVIO_SOURCE = devio-$(DEVIO_VERSION).tar.gz

DEVIO_DEPENDENCIES = uclibc 

$(eval $(call AUTOTARGETS_HOST,package,devio))

