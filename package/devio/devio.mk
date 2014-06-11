#############################################################
#
# devio for the host
#
#############################################################

DEVIO_VERSION = 1.2
DEVIO_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/devio/devio/devio-$(DEVIO_VERSION)
DEVIO_SOURCE = devio-$(DEVIO_VERSION).tar.gz

DEVIO_DEPENDENCIES = uclibc 

$(eval $(call AUTOTARGETS_HOST,package,devio))

