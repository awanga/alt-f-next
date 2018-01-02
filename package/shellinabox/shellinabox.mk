#############################################################
#
# shellinabox
#
############################################################

SHELLINABOX_VERSION = 2.20
SHELLINABOX_SITE = https://github.com/shellinabox/shellinabox/archive
SHELLINABOX_SOURCE = shellinabox-$(SHELLINABOX_VERSION).tar.gz
SHELLINABOX_SOURCE2 = v$(SHELLINABOX_VERSION).tar.gz

SHELLINABOX_LIBTOOL_PATCH = NO
SHELLINABOX_AUTORECONF = YES
SHELLINABOX_INSTALL_STAGING = NO

SHELLINABOX_DEPENDENCIES = openssh
SHELLINABOX_CONF_OPT = --disable-pam --disable-utmp

$(eval $(call AUTOTARGETS,package,shellinabox))

$(SHELLINABOX_TARGET_SOURCE):
	$(call DOWNLOAD,$(SHELLINABOX_SITE),$(SHELLINABOX_SOURCE2))
	(cd $(DL_DIR); ln -sf $(SHELLINABOX_SOURCE2) $(SHELLINABOX_SOURCE) )
	mkdir -p $(BUILD_DIR)/shellinabox-$(SHELLINABOX_VERSION)
	touch $@
