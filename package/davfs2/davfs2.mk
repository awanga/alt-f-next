#############################################################
#
# davfs2
#
#############################################################

DAVFS2_TRUNK = n

ifeq ($(DAVFS2_TRUNK),y)
DAVFS2_VERSION = 2012-07-02
DAVFS2_CVS = -d:pserver:anonymous@cvs.sv.gnu.org:/sources/davfs2
else
DAVFS2_VERSION = 1.4.6
DAVFS2_SITE = http://download.savannah.gnu.org/releases/davfs2
endif

DAVFS2_SOURCE = davfs2-$(DAVFS2_VERSION).tar.gz
DAVFS2_AUTORECONF = NO
DAVFS2_LIBTOOL_PATCH = YES
DAVFS2_INSTALL_STAGING = NO
DAVFS2_INSTALL_TARGET = YES
DAVFS2_DEPENDENCIES = uclibc neon libiconv

DAVFS2_CONF_ENV = CFLAGS+=-I$(STAGING_DIR)/usr/include/neon

# how to create the patch:
# have gnulib-tool in path (has to git clone gnulib somewhere)
# git clone git://git.savannah.gnu.org/gnulib.git
# perhaps a gnulib host-package should be created and a dependency added?
# cvs checkout davfs and make a copy of it
# edit Makefile.am, remove man from SUBDIRS:
# sed -i 's/^SUBDIRS.*/SUBDIRS = gl glpo po etc src/' Makefile.am
# edit bootstrap, comment "cd man;...":
# sed -i 's/cd man.*/#&/' bootstrap
# ./bootstrap
# find . -name \*~ -delete
# rm -rf tests autom4te.cache
# diff -Nru <plain cvs checkout> <curr dir> > davsfs2-....patch

$(eval $(call AUTOTARGETS,package,davfs2))

ifeq ($(DAVFS2_TRUNK),y)
$(DAVFS2_DIR)/.stamp_downloaded: $(DL_DIR)/$(DAVFS2_SOURCE)
	mkdir -p $(DAVFS2_DIR)
	touch $@
endif

ifeq ($(DAVFS2_TRUNK),y)
$(DL_DIR)/$(DAVFS2_SOURCE):
	mkdir -p $(DAVFS2_DIR)
	cvs $(DAVFS2_CVS) checkout -D $(DAVFS2_VERSION) davfs2
	mv davfs2 davfs2-$(DAVFS2_VERSION)
	touch davfs2-$(DAVFS2_VERSION)/configure
	chmod +x davfs2-$(DAVFS2_VERSION)/configure
	tar -cvzf davfs2-$(DAVFS2_VERSION).tar.gz davfs2-$(DAVFS2_VERSION)
	mv davfs2-$(DAVFS2_VERSION).tar.gz $(DL_DIR)
	rm -rf davfs2-$(DAVFS2_VERSION)
	touch $@
endif

$(DAVFS2_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/davfs2
	touch $@
