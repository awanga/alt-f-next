#############################################################
#
# groff
#
#############################################################
GROFF_VERSION:=1.21
GROFF_SOURCE:=groff-$(GROFF_VERSION).tar.gz
GROFF_SITE:=ftp://ftp.gnu.org/gnu/groff

# some Makefiles/script just don't honour this variables, other do.
GROFF_MAKE_ENV = TROFFBIN=troff GROFFBIN=groff GROFF_BIN_PATH="/usr/bin" GROFF_BIN_DIR="/usr/bin"

GROFF_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,groff))

# the handling (existence!) of GROFF_BIN_DIR, GROFFBIN, etc, is, well...
$(GROFF_HOOK_POST_EXTRACT):
	find $(GROFF_DIR) -name Makefile\* -exec sed -i 's/^GROFFBIN=.*/GROFFBIN=echo/' {} \;
	sed -i 's|^GROFF_BIN_DIR=.*|GROFF_BIN_DIR=/usr/bin|' $(GROFF_DIR)/contrib/pdfmark/Makefile.sub 
	touch $@