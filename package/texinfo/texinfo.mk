#############################################################
#
# texinfo
#
#############################################################

# version 4.13 is REQUIRED by the toolchain (gcc-4.3.3)

TEXINFO_VERSION = 4.13a
TEXINFO_SITE = http://ftp.gnu.org/gnu/texinfo
TEXINFO_SOURCE = texinfo-$(TEXINFO_VERSION).tar.gz

TEXINFO_AUTORECONF = NO
TEXINFO_LIBTOOL_PATCH = NO
TEXINFO_HOST_DEPENDENCIES = ncurses-host

$(eval $(call AUTOTARGETS_HOST,package,texinfo))
