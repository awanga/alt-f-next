#############################################################
#
# gnupg
#
#############################################################

#GNUPG_VERSION:=2.0.22 too may dependencies
GNUPG_VERSION:=1.4.15
GNUPG_SOURCE:=gnupg-$(GNUPG_VERSION).tar.bz2
GNUPG_SITE:=ftp://ftp.gnupg.org/gcrypt/gnupg

GNUPG_DEPENDENCIES = readline libusb libiconv

$(eval $(call AUTOTARGETS,package,gnupg))
