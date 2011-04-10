
BINS = sysctrl dns323-fw rpcinfo

all: $(BINS)

install-strip: $(BINS)
	$(STRIP) $(BINS)
	mkdir -p $(DESTDIR)/sbin/
	cp -a sysctrl $(DESTDIR)/sbin/
	cp -a dns323-fw $(DESTDIR)/usr/sbin/
	cp -a rpcinfo  $(DESTDIR)/usr/sbin/

