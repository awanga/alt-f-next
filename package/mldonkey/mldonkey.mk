#############################################################
#
# mldonkey
#
#############################################################

MLDONKEY_VERSION = 3.1.3
MLDONKEY_SOURCE = mldonkey-$(MLDONKEY_VERSION).tar.bz2
MLDONKEY_SITE =  $(BR2_SOURCEFORGE_MIRROR)/mldonkey/mldonkey/$(MLDONKEY_VERSION)
MLDONKEY_SUBDIR = mldonkey-$(MLDONKEY_VERSION)
MLDONKEY_AUTORECONF = NO
MLDONKEY_INSTALL_STAGING = NO
MLDONKEY_INSTALL_TARGET = YES
MLDONKEY_LIBTOOL_PATCH = NO
MLDONKEY_DEPENDENCIES = uclibc ocaml

MLDONKEY_CONF_OPT += --disable-option-checking
MLDONKEY_CONF_ENV = PATH=$(STAGING_DIR)/usr/bin:$(TARGET_PATH)

$(eval $(call AUTOTARGETS,package,mldonkey))


