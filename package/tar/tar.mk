#############################################################
#
# tar
#
#############################################################

TAR_VERSION:=1.32
TAR_SOURCE:=tar-$(TAR_VERSION).tar.bz2
TAR_SITE:=$(BR2_GNU_MIRROR)/tar/
TAR_DIR:=$(BUILD_DIR)/tar-$(TAR_VERSION)
TAR_CAT:=$(BZCAT)
TAR_BINARY:=src/tar
TAR_TARGET_BINARY:=bin/tar

TAR_DEPENDENCIES:=libiconv acl
#TAR_CONF_OPT += --enable-backup-scripts # conflicts with Alt-F backup
TAR_CONF_ENV += DEFAULT_ARCHIVE_FORMAT=POSIX \
		RSH=/usr/bin/ssh \
		ac_cv_func_chown_works=yes \
		gl_cv_func_chown_slash_works=yes \
		gl_cv_func_chown_follows_symlink=yes \
		gl_cv_func_chown_ctime_works=yes \
		gl_cv_func_link_follows_symlink=no \
		gl_cv_struct_dirent_d_ino=yes \
		gl_cv_func_fchownat_nofollow_works=yes \
		ac_cv_func_lstat_dereferences_slashed_symlink=yes \
		gl_cv_func_mkdir_trailing_dot_works=yes \
		gl_cv_func_gettimeofday_clobber=no \
		gl_cv_func_getcwd_path_max=no \
		gl_cv_header_working_fcntl_h=yes \
		gl_cv_func_working_utimes=yes \
		gl_cv_func_mkfifo_works=yes \
		gl_cv_func_readlink_works=yes \
		gl_cv_func_rename_dest_works=yes \
		gl_cv_func_rename_link_works=yes \
		gl_cv_func_stat_file_slash=yes \
		ac_cv_sys_file_offset_bits=64 \

ifeq ($(BR2_PACKAGE_ACL),y)
TAR_DEPENDENCIES += acl
TAR_CONF_OPTS += --with-posix-acls
else
TAR_CONF_OPTS += --without-posix-acls
endif

ifeq ($(BR2_PACKAGE_ATTR),y)
TAR_DEPENDENCIES += attr
TAR_CONF_OPTS += --with-xattrs
else
TAR_CONF_OPTS += --without-xattrs
endif

$(eval $(call AUTOTARGETS,package,tar))

$(TAR_HOOK_POST_INSTALL):
	rm -f $(TARGET_DIR)/usr/lib/rmt
	touch $@
