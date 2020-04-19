#############################################################
#
# file
#
#############################################################

FILE_VERSION:=5.32
FILE_SOURCE:=file-$(FILE_VERSION).tar.gz
FILE_SITE:=ftp://ftp.astron.com/pub/file/

FILE_LIBTOOL_PATCH = NO
FILE_INSTALL_STAGING = YES

FILE_DEPENDENCIES = uclibc zlib file-host

$(eval $(call AUTOTARGETS,package,file))

$(eval $(call AUTOTARGETS_HOST,package,file))
