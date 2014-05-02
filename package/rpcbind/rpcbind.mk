#############################################################
#
# rpcbind
#
#############################################################

# also, see this patch:
# http://lists.uclibc.org/pipermail/uclibc/2010-February/043569.html
# compiling now, after libtirpc building

RPCBIND_VERSION = 0.2.0
RPCBIND_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/rpcbind/rpcbind/$(RPCBIND_VERSION)
RPCBIND_SOURCE = rpcbind-$(RPCBIND_VERSION).tar.bz2

RPCBIND_AUTORECONF = YES
RPCBIND_INSTALL_STAGING = NO
RPCBIND_INSTALL_TARGET = YES
RPCBIND_LIBTOOL_PATCH = NO
RPCBIND_DEPENDENCIES = libtirpc

RPCBIND_CONF_ENV += CFLAGS="$(TARGET_CFLAGS) -I$(STAGING_DIR)/usr/include/tirpc/"

$(eval $(call AUTOTARGETS,package,rpcbind))

$(RPCBIND_HOOK_POST_CONFIGURE):
	(echo '#include <errno.h>'; \
	echo '#define err(exitcode, format, args...) \
		errx(exitcode, format ": %s", ## args, strerror(errno))'; \
	echo '#define errx(exitcode, format, args...) \
		{ warnx(format, ## args); exit(exitcode); }'; \
	echo '#define warn(format, args...) \
		warnx(format ": %s", ## args, strerror(errno))'; \
	echo '#define warnx(format, args...) \
		fprintf(stderr, format "\n", ## args)'; \
	) > $(RPCBIND_DIR)/src/err.h
	touch $@
