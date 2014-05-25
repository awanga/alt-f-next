#############################################################
#
# file
#
#############################################################

FILE_VERSION:=5.04
FILE_SOURCE:=file-$(FILE_VERSION).tar.gz
FILE_SITE:=ftp://ftp.astron.com/pub/file/

FILE_DEPENDENCIES = uclibc zlib file-host

# DESTDIR badly supported at install time, don't use
FILE_HOST_INSTALL_OPT = install

$(eval $(call AUTOTARGETS,package,file))

$(eval $(call AUTOTARGETS_HOST,package,file))

# DESTDIR badly supported at install time, instead specify --prefix with final destination at configure time 
$(FILE_HOST_CONFIGURE):
	$(call MESSAGE,"Host Configuring")
	cd $(FILE_HOST_DIR) && rm -f config.cache && \
	$(HOST_CONFIGURE_OPTS) \
	$(HOST_CONFIGURE_ENV) \
	$(FILE_HOST_CONF_ENV) \
	./configure \
		--prefix=$(HOST_DIR)/usr \
		--exec-prefix=$(HOST_DIR)/usr \
		--libdir=$(HOST_DIR)/usr/lib \
		--libexecdir=$(HOST_DIR)/usr/lib \
		--sysconfdir=$(HOST_DIR)/etc \
		$(DISABLE_DOCUMENTATION) \
		$(DISABLE_NLS) \
		$(DISABLE_LARGEFILE) \
		$(DISABLE_IPV6) \
		$(QUIET) $(FILE_HOST_CONF_OPT)
	$(Q)touch $@
