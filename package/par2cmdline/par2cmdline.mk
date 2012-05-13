#############################################################
#
# par2cmdline
#
#############################################################

#http://sourceforge.net/projects/parchive/files/par2cmdline/0.4/par2cmdline-0.4.tar.gz/download

PAR2CMDLINE_VERSION = 0.4
PAR2CMDLINE_SOURCE = par2cmdline-$(PAR2CMDLINE_VERSION).tar.gz
#PAR2CMDLINE_SITE = http://$(SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/parchive/files/par2cmdline/$(PAR2CMDLINE_VERSION)/
PAR2CMDLINE_SITE = http://sourceforge.net/projects/parchive/files/par2cmdline/$(PAR2CMDLINE_VERSION)
PAR2CMDLINE_AUTORECONF = NO
PAR2CMDLINE_INSTALL_STAGING = NO
PAR2CMDLINE_INSTALL_TARGET = YES
PAR2CMDLINE_LIBTOOL_PATCH = NO

PAR2CMDLINE_DEPENDENCIES = uclibc 

#PAR2CMDLINE_CONF_OPT = --disable-nls --disable-gtk --disable-gconf2 --enable-utp
#PAR2CMDLINE_CONF_ENV = LIBEVENT_CFLAGS="-I$(STAGING_DIR)/libevent2/include" \
	LIBEVENT_LIBS="-L$(STAGING_DIR)/libevent2/lib -levent2" ac_cv_prog_HAVE_CXX=yes

$(eval $(call AUTOTARGETS,package,par2cmdline))
