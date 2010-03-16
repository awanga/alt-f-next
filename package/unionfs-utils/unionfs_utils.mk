#############################################################
#
# unionfs_utils
#
#############################################################
UNIONFS_UTILS_VERSION = 0.2.1
UNIONFS_UTILS_SOURCE = unionfs_utils-$(UNIONFS_UTILS_VERSION).tar.gz
UNIONFS_UTILS_SITE = http://download.filesystems.org/unionfs/unionfs-utils-0.x/
UNIONFS_UTILS_AUTORECONF = NO
UNIONFS_UTILS_INSTALL_STAGING = NO
UNIONFS_UTILS_INSTALL_TARGET = YES
UNIONFS_UTILS_LIBTOOL_PATCH = NO
#UNIONFS_UTILS_CONF_OPT =  --disable-nls --disable-gtk

UNIONFS_UTILS_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS,package,unionfs_utils))
