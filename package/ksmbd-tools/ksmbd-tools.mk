################################################################################
#
# ksmbd-tools
#
################################################################################

KSMBD_TOOLS_VERSION = 3.4.2
KSMBD_TOOLS_SITE = $(call github,cifsd-team,ksmbd-tools,$(KSMBD_TOOLS_VERSION))
KSMBD_TOOLS_LICENSE = GPL-2.0 or later
KSMBD_TOOLS_LICENSE_FILES = COPYING
KSMBD_TOOLS_AUTORECONF = YES

KSMBD_TOOLS_DEPENDENCIES = libglib2 libnl

# Make sure kernel version >= 5.15 (support CONFIG_SMB_SERVER)
#
$(KSMBD_TOOLS_DIR)/$(KSMBD_TOOLS_KCONFIG_STAMP_DOTCONFIG): $(KSMBD_TOOLD_DIR)/.stamp_check_kernel_version

.SECONDEXPANSION:
$(KSMBD_TOOLS_DIR)/.stamp_check_kernel_version: $$(LINUX_DIR)/$$(LINUX_KCONFIG_STAMP_DOTCONFIG)
	$(Q)KVER=$(LINUX_VERSION_PROBED); \
	KVER_MAJOR=`echo $${KVER} | sed 's/^\([0-9]*\)\..*/\1/'`; \
	KVER_MINOR=`echo $${KVER} | sed 's/^[0-9]*\.\([0-9]*\).*/\1/'`; \
	if [ $${KVER_MAJOR} -lt 5 -o \( $${KVER_MAJOR} -lt 15 \) ]; then \
		printf "Linux version '%s' is too old for ksmbd-tools (needs 5.15 or later)\n" \
			"$${KVER}"; \
		exit 1; \
	fi
	$(Q)touch $(@)

$(eval $(autotools-package))
