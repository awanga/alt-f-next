#############################################################
#
# lftp
#
#############################################################

LFTP_VERSION:=4.6.1
LFTP_SOURCE:=lftp-$(LFTP_VERSION).tar.gz
LFTP_SITE:=http://lftp.yar.ru/ftp

LFTP_LIBTOOL_PATCH = NO
LFTP_DEPENDENCIES = readline expat libiconv gettext openssl

LFTP_CONF_OPT = --without-gnutls --with-openssl

$(eval $(call AUTOTARGETS,package,lftp))
