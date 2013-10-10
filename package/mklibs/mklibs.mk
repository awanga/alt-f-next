#############################################################
#
# mklibs for the host
#
#############################################################

MKLIBS_VERSION = 0.1.31
MKLIBS_SOURCE = mklibs_$(MKLIBS_VERSION).tar.gz
MKLIBS_SITE = http://snapshot.debian.org/archive/debian/20101225T025119Z/pool/main/m/mklibs

MKLIBS_DEPENDENCIES = uclibc

$(eval $(call AUTOTARGETS_HOST,package,mklibs))

$(MKLIBS_HOST_HOOK_POST_EXTRACT):
	sed -i '/#include <fcntl.h>/i#include <unistd.h>' \
	$(MKLIBS_HOST_DIR)/src/mklibs-readelf/elf.cpp
	touch $@
