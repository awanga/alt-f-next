#############################################################
#
# a2ps
#
#############################################################
A2PS_VERSION = 4.14
A2PS_SOURCE = a2ps-$(A2PS_VERSION).tar.gz
A2PS_SITE = $(BR2_GNU_MIRROR)/a2ps
A2PS_INSTALL_STAGING = YES
A2PS_INSTALL_TARGET = YES
A2PS_DEPENDENCIES = uclibc gperf-host file

A2PS_CONF_ENV = ac_cv_prog_EMACS=no ac_cv_path_file_prog=/usr/bin/file

$(eval $(call AUTOTARGETS,package,a2ps))

$(A2PS_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/emacs
	touch $@
