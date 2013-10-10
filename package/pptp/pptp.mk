#############################################################
#
# pptp
#
#############################################################

#http://sourceforge.net/projects/pptpclient/files/pptp/pptp-1.7.2/pptp-1.7.2.tar.gz/download

#http://switch.dl.sourceforge.net/project/pptpclient/pptp/pptp-1.7.2/pptp-1.7.2.tar.gz

PPTP_VERSION:=1.7.2
PPTP_SOURCE:=pptp-$(PPTP_VERSION).tar.gz
PPTP_SITE:=$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/project/pptpclient/pptp/pptp-$(PPTP_VERSION)

PPTP_DEPENDENCIES = uclibc pppd
PPTP_MAKE_OPT = $(TARGET_CONFIGURE_OPTS) $(TARGET_CONFIGURE_ARGS) OPTIMIZE="$(TARGET_CFLAGS)" DEBUG=""
PPTP_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,pptp))

$(PPTP_TARGET_CONFIGURE):
	sed -i 's|install -o root|install|' $(PPTP_DIR)/Makefile
	sed -i 's|#include <stropts.h>|/*&*/|' $(PPTP_DIR)/pptp_compat.c
	touch $@
