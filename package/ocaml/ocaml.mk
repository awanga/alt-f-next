#############################################################
#
# ocaml
#
#############################################################

OCAML_VERSION = 3.12.1
OCAML_SOURCE = ocaml-$(OCAML_VERSION).tar.gz
OCAML_SITE = http://caml.inria.fr/pub/distrib/ocaml-3.12
OCAML_INSTALL_STAGING = YES
OCAML_INSTALL_TARGET = NO
OCAML_LIBTOOL_PATCH = NO
OCAML_DEPENDENCIES = uclibc host-ocaml
OCAML_DIR = $(BUILD_DIR)/ocaml-$(OCAML_VERSION)
OCAML_HOST_DIR:=$(BUILD_DIR)/ocaml-$(OCAML_VERSION)-host

$(DL_DIR)/$(OCAML_SOURCE):
	$(call DOWNLOAD,$(OCAML_SITE),$(OCAML_SOURCE))

$(OCAML_DIR)/.unpacked: $(DL_DIR)/$(OCAML_SOURCE)
	$(INFLATE$(suffix $(OCAML_SOURCE))) $< | tar -C $(BUILD_DIR) $(TAR_OPTIONS) -
	toolchain/patch-kernel.sh $(OCAML_DIR) package/ocaml/ \*.patch
	sed -i 's/cross=.*/cross=arm-linux-uclibcgnueabi-/' $(OCAML_DIR)/configure
	touch $@

$(OCAML_DIR)/.configured: $(OCAML_HOST_DIR)/.installed $(OCAML_DIR)/.unpacked
	(cd $(OCAML_DIR); \
		$(HOST_CONFIGURE_OPTS) \
		CFLAGS="$(HOST_CFLAGS)" \
		LDFLAGS="$(HOST_LDFLAGS)" \
		./configure \
		--prefix "$(STAGING_DIR)/usr" \
		--no-tk \
	)
	touch $@

$(OCAML_DIR)/.build: $(OCAML_DIR)/.configured
	PATH=$(TARGET_PATH) $(MAKE) -j1 -C $(OCAML_DIR) cross
	touch $@

$(OCAML_DIR)/.installed: $(OCAML_DIR)/.build
	PATH=$(TARGET_PATH) $(MAKE) -j1 -C $(OCAML_DIR) installcross
	touch $@

# ocaml for the host

$(OCAML_HOST_DIR)/.unpacked: $(DL_DIR)/$(OCAML_SOURCE)
	mkdir -p $(OCAML_HOST_DIR)
	$(INFLATE$(suffix $(OCAML_SOURCE))) $< | \
		$(TAR) $(TAR_STRIP_COMPONENTS)=1 -C $(OCAML_HOST_DIR) $(TAR_OPTIONS) -
	touch $@

$(OCAML_HOST_DIR)/.configured: $(OCAML_HOST_DIR)/.unpacked
	(cd $(OCAML_HOST_DIR); \
		$(HOST_CONFIGURE_OPTS) \
		CFLAGS="$(HOST_CFLAGS)" \
		LDFLAGS="$(HOST_LDFLAGS)" \
		./configure \
		--prefix "$(HOST_DIR)/usr" \
		--no-tk \
	)
	touch $@

$(OCAML_HOST_DIR)/.build: $(OCAML_HOST_DIR)/.configured
	$(MAKE) -j1 -C $(OCAML_HOST_DIR) world.opt
	touch $@

$(OCAML_HOST_DIR)/.installed: $(OCAML_HOST_DIR)/.build
	$(HOST_MAKE_ENV) $(MAKE) -j1 -C $(OCAML_HOST_DIR) install
	touch $@

host-ocaml: $(OCAML_HOST_DIR)/.installed

host-ocaml-build: $(OCAML_HOST_DIR)/.build

host-ocaml-configure: $(OCAML_HOST_DIR)/.configured

host-ocaml-source: ocaml-source

host-ocaml-clean:
	rm -f $(addprefix $(OCAML_HOST_DIR)/,.unpacked .configured .build .installed)
	-$(MAKE) -C $(OCAML_HOST_DIR) uninstall
	-$(MAKE) -C $(OCAML_HOST_DIR) clean

host-ocaml-dirclean:
	rm -rf $(OCAML_HOST_DIR)

ocaml-extract: $(OCAML_DIR)/.unpacked

ocaml-configure: $(OCAML_DIR)/.configured

ocaml-build: $(OCAML_DIR)/.build

ocaml: $(OCAML_DIR)/.installed

ifeq ($(BR2_PACKAGE_OCAML),y)
TARGETS+=ocaml
endif