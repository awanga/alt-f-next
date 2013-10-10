#############################################################
#
# cadaver
#
#############################################################

CADAVER_VERSION:=0.23.3
CADAVER_SOURCE:=cadaver-$(CADAVER_VERSION).tar.gz
CADAVER_SITE:=http://www.webdav.org/cadaver

CADAVER_DEPENDENCIES = ncurses readline libiconv neon uclibc
CADAVER_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,cadaver))

$(CADAVER_HOOK_POST_CONFIGURE):
	echo "#define HAVE_LOCALE_H 1" >> $(CADAVER_DIR)/config.h
	touch $@