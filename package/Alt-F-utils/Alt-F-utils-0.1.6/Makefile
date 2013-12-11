
BINS = sysctrl dns323-fw rpcinfo unbuffer.so

all: $(BINS)

clean:
	$(RM) $(BINS) *.o

install install-strip: $(BINS)
	$(STRIP) $(BINS)
	mkdir -p $(DESTDIR)/usr/sbin $(DESTDIR)/usr/lib
	cp -a sysctrl $(DESTDIR)/usr/sbin/
	cp -a dns323-fw $(DESTDIR)/usr/sbin/
	cp -a rpcinfo  $(DESTDIR)/usr/sbin/
	#cp -a unbuffer.so $(DESTDIR)/usr/lib/

unbuffer.so: unbuffer.c
	$(CC) unbuffer.c -fPIC -shared -o $@
