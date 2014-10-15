#############################################################
#
# git
#
#############################################################

GIT_VERSION = 2.1.2
GIT_SOURCE = git-$(GIT_VERSION).tar.xz
GIT_SITE = https://www.kernel.org/pub/software/scm/git

GIT_INSTALL_STAGING = NO
GIT_INSTALL_TARGET = YES
GIT_DEPENDENCIES = uclibc openssl libcurl expat pcre perl-host

GIT_CONF_ENV = ac_cv_fread_reads_directories=yes \
	ac_cv_snprintf_returns_bogus=yes 

GIT_CONF_OPT = --without-python --without-tcltk \
	-with-libpcre --with-perl=$(HOST_DIR)/usr/bin/perl

GIT_MAKE_OPT = CHARSET_LIB=-lcharset

GIT_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,git))

$(GIT_HOOK_POST_INSTALL):
	for i in $$(grep -lr "$(HOST_DIR)/usr/bin/perl" $(TARGET_DIR)/usr/lib/git-core); do \
		sed -i "s|$(HOST_DIR)/usr/bin/perl|/usr/bin/perl|" $$i; \
	done
	touch $@
