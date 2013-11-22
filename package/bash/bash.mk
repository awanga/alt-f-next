#############################################################
#
# bash
#
#############################################################

BASH_VERSION:=4.2
BASH_SOURCE:=bash-$(BASH_VERSION).tar.gz
BASH_SITE:=$(BR2_GNU_MIRROR)/bash
BASH_CAT:=$(ZCAT)
BASH_DIR:=$(BUILD_DIR)/bash-$(BASH_VERSION)
BASH_BINARY:=bash
BASH_TARGET_BINARY:=bin/bash
BASH_DEPENDENCIES:=ncurses

ifeq ($(BR2_ENABLE_DEBUG),y)
BASH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install
else
BASH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install-strip STRIPPROG="$(STRIPCMD)"
endif

BASH_CONF_ENV = ac_cv_func_setvbuf_reversed=no \
		ac_cv_have_decl_sys_siglist=yes \
		bash_cv_job_control_missing=present \
		bash_cv_sys_named_pipes=present \
		bash_cv_unusable_rtsigs=no \
		bash_cv_func_ctype_nonascii=yes \
		bash_cv_decl_under_sys_siglist=yes \
		bash_cv_ulimit_maxfds=yes \
		bash_cv_getcwd_malloc=yes \
		bash_cv_func_sigsetjmp=present \
		bash_cv_printf_a_format=yes \
		ac_cv_path_install=./support/install.sh

BASH_CONF_OPT = $(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
		--with-curses \
		--enable-alias \
		--without-bash-malloc

$(eval $(call AUTOTARGETS,package,bash))
