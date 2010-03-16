#############################################################
#
# msmtp
#
#############################################################
MSMTP_VERSION = 1.4.19
MSMTP_SOURCE = msmtp-$(MSMTP_VERSION).tar.bz2
MSMTP_SITE = http://downloads.sourceforge.net/project/msmtp/msmtp/$(MSMTP_VERSION)
#MSMTP_AUTORECONF = NO
MSMTP_INSTALL_STAGING = NO
MSMTP_INSTALL_TARGET = YES
MSMTP_BINARY:=src/msmtp
MSMTP_TARGET_BINARY:=usr/bin/msmtp

# somehow "configure" tries to "link" against the system /usr/lib/libssl.so
# --without-libssl-prefix makes it use -lssl, and buildroot adds the necessary -L
# But "make install" creates arm-linux-msmtp!!! the --program-transform-name="echo" hacks it (the wrong way, but I'm sick!)
MSMTP_CONF_OPT = --without-libssl-prefix --program-transform-name="echo"

MSMTP_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS,package,msmtp))
