#############################################################
#
# kernel-modules
#
#############################################################

KERNEL_MODULES_VERSION:=4.4.86

# this is a dummy target, it is here just to have BR2_PACKAGE_KERNEL_MODULES defined
kernel-modules: uclibc

#############################################################
#
# Toplevel Makefile options
#
#############################################################
ifeq ($(BR2_PACKAGE_KERNEL_MODULES),y)
TARGETS+=kernel-modules
endif
