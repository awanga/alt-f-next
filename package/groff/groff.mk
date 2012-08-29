#############################################################
#
# groff
#
#############################################################
GROFF_VERSION:=1.21
GROFF_SOURCE:=groff-$(GROFF_VERSION).tar.gz
GROFF_SITE:=ftp://ftp.gnu.org/gnu/groff
#GROFF_INSTALL_STAGING = NO

GROFF_MAKE_ENV = TROFFBIN=troff GROFFBIN=groff GROFF_BIN_PATH=" "

GROFF_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,groff))
