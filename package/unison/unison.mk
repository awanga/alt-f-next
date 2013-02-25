#############################################################
#
# unison
#
#############################################################

#UNISON_VERSION = 2.40.102
UNISON_VERSION = 2.40.63
UNISON_SOURCE = unison-$(UNISON_VERSION).tar.gz
UNISON_SITE = http://www.seas.upenn.edu/~bcpierce/unison//download/releases/unison-$(UNISON_VERSION)
UNISON_AUTORECONF = NO
UNISON_INSTALL_STAGING = NO
UNISON_INSTALL_TARGET = YES
UNISON_LIBTOOL_PATCH = NO
UNISON_DEPENDENCIES = uclibc ocaml

$(eval $(call AUTOTARGETS,package,unison))


