###########################################################
#
# dropbear
#
###########################################################

DROPBEAR_VERSION = 2019.78
DROPBEAR_SOURCE = dropbear-$(DROPBEAR_VERSION).tar.bz2
DROPBEAR_SITE = https://matt.ucc.asn.au/dropbear/releases
DROPBEAR_DEPENDENCIES = uclibc zlib
DROPBEAR_TARGET_BINS = dbclient dropbearkey dropbearconvert scp ssh
DROPBEAR_MAKE =	$(MAKE) MULTI=1 SCPPROGRESS=1 \
		PROGRAMS="dropbear dbclient dropbearkey dropbearconvert scp"

DROPBEAR_CONF_ENV = CFLAGS="$(TARGET_CFLAGS) $(BR2_PACKAGE_DROPBEAR_OPTIM)"
DROPBEAR_CONF_OPT = --disable-wtmp --disable-lastlog --disable-harden 

$(eval $(call AUTOTARGETS,package,dropbear))

$(DROPBEAR_HOOK_POST_EXTRACT):
	echo '#define SFTPSERVER_PATH "/usr/lib/sftp-server"' > $(DROPBEAR_DIR)/localoptions.h
	echo '#define DROPBEAR_X11FWD 0' >> $(DROPBEAR_DIR)/localoptions.h
	touch $@

$(DROPBEAR_TARGET_INSTALL_TARGET):
	$(call MESSAGE,"Installing to target")
	$(INSTALL) -m 755 $(DROPBEAR_DIR)/dropbearmulti \
		$(TARGET_DIR)/usr/sbin/dropbear
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/dbclient
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/dropbearkey
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/dropbearconvert
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/scp-dropbear
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/scp
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/ssh-dropbear
	ln -snf ../sbin/dropbear $(TARGET_DIR)/usr/bin/ssh
	touch $@

$(DROPBEAR_TARGET_UNINSTALL):
	$(call MESSAGE,"Uninstalling")
	rm -f $(TARGET_DIR)/usr/sbin/dropbear
	rm -f $(addprefix $(TARGET_DIR)/usr/bin/, $(DROPBEAR_TARGET_BINS))
	#rm -f $(TARGET_DIR)/etc/init.d/S50dropbear
	rm -f $(DROPBEAR_TARGET_INSTALL_TARGET) $(DROPBEAR_HOOK_POST_INSTALL)

