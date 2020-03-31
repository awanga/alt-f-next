#############################################################
#
# wsdd2
#
#############################################################

WSDD2_VERSION = 1.8
WSDD2_SOURCE = wsdd2-$(WSDD2_VERSION).tar.gz
WSDD2_SITE = https://github.com/Andy2244/wsdd2/archive

WSDD2_DEPENDENCIES = uclibc

WSDD2_MAKE_ENV := CC="$(TARGET_CC) $(TARGET_CFLAGS)" STRIP="$(TARGET_STRIP)"
#WSDD2_INSTALL_TARGET_OPT := DESTDIR=$(TARGET_DIR) install

$(eval $(call AUTOTARGETS,package,wsdd2))

$(WSDD2_TARGET_SOURCE):
	$(call DOWNLOAD,$(WSDD2_SITE),master.tar.gz)
	(cd $(DL_DIR); ln -sf master.tar.gz wsdd2-$(WSDD2_VERSION).tar.gz )
	mkdir -p $(BUILD_DIR)/wsdd2-$(WSDD2_VERSION)
	touch $@

$(WSDD2_TARGET_CONFIGURE):
	touch $@

$(WSDD2_HOOK_POST_CONFIGURE):
	(echo '#include <errno.h>'; \
	echo '#define err(exitcode, format, args...) \
		errx(exitcode, format ": %s", ## args, strerror(errno))'; \
	echo '#define errx(exitcode, format, args...) \
		{ warnx(format, ## args); exit(exitcode); }'; \
	echo '#define warn(format, args...) \
		warnx(format ": %s", ## args, strerror(errno))'; \
	echo '#define warnx(format, args...) \
		fprintf(stderr, format "\n", ## args)'; \
	) > $(WSDD2_DIR)/err.h
	$(SED) 's/<err.h>/"err.h"/' $(WSDD2_DIR)/wsdd.h
	touch $@

$(WSDD2_TARGET_INSTALL_TARGET):
	(cd $(WSDD2_DIR); $(INSTALL) wsdd2 $(TARGET_DIR)/usr/sbin)
	touch $@
