
BINS = sysctrl dns323-fw rpcinfo dns320l-daemon
# unbuffer.so

all: $(BINS)

clean:
	$(RM) $(BINS) *.o

install install-strip: $(BINS)
	$(STRIP) $(BINS)
	mkdir -p $(DESTDIR)/usr/sbin
	cp -a $(BINS) $(DESTDIR)/usr/sbin/
	#mkdir -p $(DESTDIR)/usr/lib
	#cp -a unbuffer.so $(DESTDIR)/usr/lib/

uninstall:
	cd $(DESTDIR)/usr/sbin && rm -f $(BINS)

unbuffer.so: unbuffer.c
	$(CC) unbuffer.c -fPIC -shared -o $@
