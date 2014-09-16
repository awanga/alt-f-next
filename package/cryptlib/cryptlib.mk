#############################################################
#
# cryptlib
#
#############################################################

CRYPTLIB_VERSION:=342
CRYPTLIB_SOURCE:=cl$(CRYPTLIB_VERSION).zip
CRYPTLIB_SITE:=ftp://ftp.franken.de/pub/crypt/cryptlib

CRYPTLIB_LIBTOOL_PATCH = NO
CRYPTLIB_INSTALL_STAGING = YES

CRYPTLIB_MAKE_OPT = target-linux-arm

CRYPTLIB_MAKE = $(MAKE1)

CRYPTLIB_MAKE_ENV = \
	CC="$(TARGET_CC)" \
	CRYPTLIB_CFLAGS="$(TARGET_CFLAGS)" \
	AR=$(TARGET_AR) \
	LD=$(TARGET_LD) \
	STRIP=$(TARGET_STRIP)

$(eval $(call AUTOTARGETS,package,cryptlib))

$(CRYPTLIB_TARGET_EXTRACT):
	if ! which unzip; then /bin/echo -e "\n\nYou must install 'unzip' on your build machine\n"; fi
	unzip -a $(DL_DIR)/$(CRYPTLIB_SOURCE) -d $(CRYPTLIB_DIR)
	touch $@

$(CRYPTLIB_TARGET_CONFIGURE):
	touch $@

# INCOMPLETE. need source code changes:
#
#makefile:
#
#CFLAGS		= $(CRYPTLIB_CFLAGS) -c -D__UNIX__ -DNDEBUG -I.
#
## still to try -DCONFIG_SLOW_CPU
#
#target-linux-arm:
#	@make directories
#	@make toolscripts
#	make $(XDEFINES) OSNAME=Linux \
3		CFLAGS="$(CFLAGS) -DCONFIG_DATA_LITTLEENDIAN -D_REENTRANT \
#		-DCONFIG_CONSERVE_MEMORY -DUSE_ERRMSGS"
#	make $(SLIBNAME) OBJPATH=$(OBJPATH) CROSSCOMPILE=1 OSNAME=Linux
#
#zlib/adler32.c:
#// jc: uLong ZEXPORT adler32_combine64(uLong adler1, uLong adler2, z_off64_t len2)	/* pcg */
#uLong ZEXPORT adler32_combine64(uLong adler1, uLong adler2, off64_t len2)	/* pcg */
