build:
	$(CC) -c crc32.c -o crc32.o
	$(CC) -c mkimage.c -o mkimage.o
	$(CC) -o mkimage *.o

clean:
	rm -f mkimage *.o

install:
	install -d $(DESTDIR)/usr/bin
	install -s mkimage $(DESTDIR)/usr/bin
