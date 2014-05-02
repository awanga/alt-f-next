#############################################################
#
# file
#
#############################################################

FILE_VERSION:=5.04
FILE_SOURCE:=file-$(FILE_VERSION).tar.gz
FILE_SITE:=ftp://ftp.astron.com/pub/file/

FILE_DEPENDENCIES = uclibc zlib file-host

FILE_HOST_CONF_OPT = --prefix=$(HOST_DIR)/usr --datarootdir=/usr/share \
	--includedir=/usr/include --disable-shared

$(eval $(call AUTOTARGETS,package,file))

$(eval $(call AUTOTARGETS_HOST,package,file))
