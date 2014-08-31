#############################################################
#
# nano
#
#############################################################

NANO_VERSION:=2.2.6
NANO_SOURCE:=nano-$(NANO_VERSION).tar.gz
NANO_SITE:=http://www.nano-editor.org/dist/v2.2/

NANO_CAT:=$(ZCAT)
NANO_DEPENDENCIES = ncurses groff-host

NANO_CONF_OPT = --program-prefix=''

$(eval $(call AUTOTARGETS,package/editors,nano))
