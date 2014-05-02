#############################################################
#
# libtirpc
#
#############################################################

# patches from from the BuildRoot site
# still fails when installing to target, as it wants to strip rpcgen,
# which is in host binary, not a target binary

LIBTIRPC_VERSION = 0.2.2
LIBTIRPC_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/libtirpc/libtirpc/$(LIBTIRPC_VERSION)
LIBTIRPC_SOURCE = libtirpc-$(LIBTIRPC_VERSION).tar.bz2

LIBTIRPC_AUTORECONF = YES
LIBTIRPC_INSTALL_STAGING = YES
LIBTIRPC_INSTALL_TARGET = YES
LIBTIRPC_LIBTOOL_PATCH = NO

LIBTIRPC_CONF_ENV = CFLAGS="$(TARGET_CFLAGS) -DGQ"
LIBTIRPC_DEPENDENCIES = host-pkgconfig

$(eval $(call AUTOTARGETS,package,libtirpc))

$(LIBTIRPC_HOOK_POST_CONFIGURE):
	(echo '#include <errno.h>'; \
	echo '#define err(exitcode, format, args...) \
		errx(exitcode, format ": %s", ## args, strerror(errno))'; \
	echo '#define errx(exitcode, format, args...) \
		{ warnx(format, ## args); exit(exitcode); }'; \
	echo '#define warn(format, args...) \
		warnx(format ": %s", ## args, strerror(errno))'; \
	echo '#define warnx(format, args...) \
		fprintf(stderr, format, ## args)'; \
	) > $(LIBTIRPC_DIR)/err.h
	touch $@
