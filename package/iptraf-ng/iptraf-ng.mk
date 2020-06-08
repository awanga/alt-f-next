################################################################################
#
# iptraf-ng
#
################################################################################

IPTRAF_NG_VERSION = 1.1.4
IPTRAF_NG_SITE = https://src.fedoraproject.org/lookaside/pkgs/iptraf-ng/iptraf-ng-1.1.4.tar.gz/md5/de27cfeeede96e2acfb0edc8439b034a
IPTRAF_NG_LICENSE = GPL-2.0+
IPTRAF_NG_LICENSE_FILES = LICENSE
IPTRAF_NG_DEPENDENCIES = ncurses

IPTRAF_NG_MAKE_ENV = \
	NCURSES_LDFLAGS="-lpanel -lncurses"

IPTRAF_NG_CONF_ENV = \
	CFLAGS="$(TARGET_CFLAGS) -D_GNU_SOURCE"

$(eval $(autotools-package))
