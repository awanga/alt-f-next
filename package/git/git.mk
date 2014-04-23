#############################################################
#
# git
#
#############################################################
GIT_VERSION = 1.7.7
GIT_SOURCE = git-$(GIT_VERSION).tar.gz
GIT_SITE = http://git-core.googlecode.com/files/
GIT_INSTALL_STAGING = NO
GIT_INSTALL_TARGET = YES
GIT_DEPENDENCIES = uclibc openssl libcurl expat pcre perl-host

GIT_CONF_ENV = ac_cv_fread_reads_directories=yes \
	ac_cv_snprintf_returns_bogus=yes 

GIT_CONF_OPT = --without-python --without-tcltk \
	-with-libpcre --with-perl=$(HOST_DIR)/usr/bin/perl

#GIT_MAKE_ENV = NO_PERL=no

GIT_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,git))

$(GIT_HOOK_POST_INSTALL):
	for i in $$(grep -lr "$(HOST_DIR)/usr/bin/perl" $(TARGET_DIR)/usr/lib/git-core); do \
		sed -i "s|$(HOST_DIR)/usr/bin/perl|/usr/bin/perl|" $$i; \
	done
	touch $@
