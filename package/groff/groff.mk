#############################################################
#
# groff
#
#############################################################

GROFF_VERSION:=1.22.2
GROFF_SOURCE:=groff-$(GROFF_VERSION).tar.gz
GROFF_SITE:=$(BR2_GNU_MIRROR)/groff

# some Makefiles/script just don't honour this variables, other do.
GROFF_MAKE_ENV = TROFFBIN=troff GROFFBIN=groff GROFF_BIN_PATH="/usr/bin" GROFF_BIN_DIR="/usr/bin"

GROFF_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

# groff DESTDIR seems to be broken (does --prefix becomes hardcoded?)
GROFF_HOST_CONF_OPT = --prefix=$(HOST_DIR)/usr \
	--exec-prefix=$(HOST_DIR)/usr \
	--libdir=$(HOST_DIR)/usr/lib \
	--libexecdir=$(HOST_DIR)/usr/lib \
	--without-x

GROFF_HOST_INSTALL_OPT = install

$(eval $(call AUTOTARGETS,package,groff))

$(eval $(call AUTOTARGETS_HOST,package,groff))

# the handling (existence!) of GROFF_BIN_DIR, GROFFBIN, etc, is, well...
$(GROFF_HOOK_POST_EXTRACT):
	find $(GROFF_DIR) -name Makefile\* -exec sed -i 's/^GROFFBIN=.*/GROFFBIN=echo/' {} \;
	sed -i 's|^GROFF_BIN_DIR=.*|GROFF_BIN_DIR=/usr/bin|' $(GROFF_DIR)/contrib/pdfmark/Makefile.sub 
	touch $@

# dont install html nor pdf docs
$(GROFF_HOOK_POST_CONFIGURE):
	sed -i -e 's/^make_html=.*/make_html=/' \
		-e 's/^make_install_html=.*/make_install_html=/' \
		-e 's/^make_pdfdoc=.*/make_pdfdoc=/' \
		-e 's/^make_install_pdfdoc=.*/make_install_pdfdoc=/' \
		$(GROFF_DIR)/Makefile
	touch $@
