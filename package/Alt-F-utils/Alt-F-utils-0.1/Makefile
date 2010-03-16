
BINS = sysctrl dns323-fw rpcinfo

all: $(BINS)

install-strip: $(BINS)
	$(STRIP) $(BINS)
	cp -a sysctrl $(DESTDIR)/sbin/
	cp -a dns323-fw $(DESTDIR)/usr/sbin/
	cp -a rpcinfo  $(DESTDIR)/usr/sbin/

