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
GIT_DEPENDENCIES = uclibc openssl libcurl expat

GIT_CONF_ENV = ac_cv_c_c99_format=no ac_cv_fread_reads_directories=yes ac_cv_snprintf_returns_bogus=yes 

GIT_CONF_OPT = --without-python --without-tcltk

GIT_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,git))
