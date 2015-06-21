#############################################################
#
# tcsh
#
#############################################################

TCSH_VERSION:=6.18.01
TCSH_SOURCE:=tcsh-$(TCSH_VERSION).tar.gz
TCSH_SITE:=ftp://ftp.astron.com/pub/tcsh/old

TCSH_DEPENDENCIES = ncurses libiconv uclibc

$(eval $(call AUTOTARGETS,package,tcsh))
