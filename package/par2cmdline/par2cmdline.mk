#############################################################
#
# par2cmdline
#
#############################################################

PAR2CMDLINE_VERSION = 0.4
PAR2CMDLINE_SOURCE = par2cmdline-$(PAR2CMDLINE_VERSION).tar.gz
PAR2CMDLINE_SITE = $(BR2_SOURCEFORGE_MIRROR)/project/parchive/par2cmdline/$(PAR2CMDLINE_VERSION)

PAR2CMDLINE_AUTORECONF = NO
PAR2CMDLINE_INSTALL_STAGING = NO
PAR2CMDLINE_INSTALL_TARGET = YES
PAR2CMDLINE_LIBTOOL_PATCH = NO

PAR2CMDLINE_DEPENDENCIES = uclibc 

#PAR2CMDLINE_CONF_OPT = --disable-nls --disable-gtk --disable-gconf2 --enable-utp
#PAR2CMDLINE_CONF_ENV = LIBEVENT_CFLAGS="-I$(STAGING_DIR)/libevent2/include" \
	LIBEVENT_LIBS="-L$(STAGING_DIR)/libevent2/lib -levent2" ac_cv_prog_HAVE_CXX=yes

$(eval $(call AUTOTARGETS,package,par2cmdline))
