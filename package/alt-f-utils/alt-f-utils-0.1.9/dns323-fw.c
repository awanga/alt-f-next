/*
 * Copyright Joao Cardoso 2009, 2010, 2011, 2012, 2013
 * Licence: GPLv2
 * 
 * -Split a vendor firmware file into its kernel/initramfs/defaults components
 * -Merge a kernel/initramfs/defaults together into a vendor compatible firmware file
 *
 * Inspired in Matt's Palmer firmware-tools-0.3, written in Ruby:
 * http://theshed.hezmatt.org/dns323-firmware-tools/
 *
 * and Conceptronic merge-1.04.tar.gz, distributed together with the
 * CH3SNAS_GPL-1.04.tar.gz tarball for their CH3SNAS product:
 * http://www.conceptronic.net
 * 
 * and Magnus Olsen work on dns320flash.c
 * http://sourceforge.net/p/dns320/code/HEAD/tree/trunk/dns320_GPL/merge/dns320flash.c
 */

#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <libgen.h>
#include <stdint.h>

typedef unsigned long ulong;
typedef unsigned char uchar;

#define BLOCK_SIZE 0x10000 /* 65536d */
#define SIG_LEN 12
#define RESERVED64 7
#define RESERVED128 59

typedef struct {
	uint32_t kernel_off;
	uint32_t kernel_len;
	uint32_t initramfs_off;
	uint32_t initramfs_len;
	uint32_t defaults_off;
	uint32_t defaults_len;
	uint32_t kernel_checksum;
	uint32_t initramfs_checksum;
	uint32_t defaults_checksum;

	uchar magic_num[SIG_LEN];
	uchar product_id;
	uchar custom_id;
	uchar model_id;
	uchar sub_id;
	uchar NewVersion;
	
	uchar reserved[RESERVED64];	//all structure is 64 bytes
	uint32_t Next_offset;
} CONTROL_HEADER_64;

typedef struct {
	uint32_t kernel_off;
	uint32_t kernel_len;
	uint32_t initramfs_off;
	uint32_t initramfs_len;
	uint32_t sqimage_off;
	uint32_t sqimage_len;	
	uint32_t defaults_off;
	uint32_t defaults_len;
	uint32_t kernel_checksum;
	uint32_t initramfs_checksum;
	uint32_t sqimage_checksum;
	uint32_t defaults_checksum;
	
	uchar magic_num[SIG_LEN];
	uchar product_id;
	uchar custom_id;
	uchar model_id;
	uchar sub_id;
	uchar NewVersion;
	
	uchar reserved[RESERVED128];	//all structure is 128 bytes
	uint32_t Next_offset;
} CONTROL_HEADER_128;

typedef struct {
	uint32_t kernel_off;
	uint32_t kernel_len;
	uint32_t kernel_checksum;
	
	uint32_t initramfs_off;
	uint32_t initramfs_len;
	uint32_t initramfs_checksum;
	
	uint32_t sqimage_off;
	uint32_t sqimage_len;	
	uint32_t sqimage_checksum;
	
	uint32_t defaults_off;
	uint32_t defaults_len;
	uint32_t defaults_checksum;

	uint32_t Next_offset;

	uchar product_id;
	uchar custom_id;
	uchar model_id;
	uchar sub_id;
	uchar NewVersion;
	
	int type;	/* 64 or 128 bytes header */
	int sig_num; /* signature index */
} MY_CONTROL_HEADER;

typedef struct {
	uchar		Directory[32];
	uchar		FileName[32];

	uint16_t	chmod;
	uchar		execute;
	uchar		reserved[13];

	uint32_t 	offset;
	uint32_t 	len;
	uint32_t 	checksum;
	uint32_t 	Next_offset;
} EXTEND_HEADER;

typedef struct {
	int idx;
	int size; /* file header size, 64 or 128 bytes */
	ulong kernel_max; /* max size of kernel */
	ulong initramfs_max;
	ulong sqimage_max;
	ulong defaults_max;
	uchar signature[SIG_LEN];
} sig_t;

sig_t signatures[] = {
	{0, 64, 1572864, 6488064, 0, 65536, "\x55\xAA" "FrodoII" "\x00\x55\xAA"},	/* DNS-323 */
	{1, 64, 1572864, 10485760, 0, 131072, "\x55\xAA" "Chopper" "\x00\x55\xAA"},	/* DNS-321 */
	{2, 64, 1572864, 14417920, 0, 131072, "\x55\xAA" "Gandolf" "\x00\x55\xAA"},	/* DNS-343 */
	{3, 128, 5242880, 5242880, 106954752, 5242880, "\x55\xAA" "DNS-325" "\x00\x55\xAA"},	/* DNS-325-A1A2 */
	{4, 128, 5242880, 5242880, 106954752, 5242880, "\x55\xAA" "DNS323D1" "\x55\xAA"},	/* DNS-320-A1A2 */
	{5, 128, 5242880, 5242880, 104857600, 5242880, "\x55\xAA" "DNS320B" "\x00\x55\xAA"},	/* DNS-320-B1 */
	{6, 128, 5242880, 5242880, 104857600, 5242880, "\x55\xAA" "DNS320L" "\x00\x55\xAA"},	/* DNS-320L */
	{7, 128, 5242880, 5242880, 81788928, 10485760, "\x55\xAA" "DNS327L" "\x00\x55\xAA"}	/* DNS-327L */
};

int nsig = sizeof(signatures)/sizeof(sig_t);

char *kernel = NULL, *initramfs = NULL, *sqimage = NULL, *defaults = NULL, *fw = NULL;
uchar product = 1, custom = 2, model = 3, sub = 4, version = 5, type = 0, quiet = 0;

int readwrite(int fdo, int fdi, ulong off, ulong sz, uint32_t *chk) {
	static char *buf = NULL;

	if (buf == NULL) {
		if ((buf = (char *) malloc(BLOCK_SIZE)) == NULL) {
			perror("malloc");
			return -1;
		}
	}

	if (lseek(fdi, off, SEEK_SET) < 0)
		return -1;

	int i=0, j, k, n;
	uint32_t lchk = 0;
	uint32_t *bp;
  
	while(i < sz) {
		k = sz - i > BLOCK_SIZE ? BLOCK_SIZE : sz - i;
		n = read(fdi, buf, k);

		if (n == 0)
			break;

		if (n < 0)
			return -1;
/*	
	if (write(fdo, buf, n) < 0)
		return -1;
*/
	/* some D-Link fw files (DNS-320/325) have inconsistent components size, i.e.,
	 * the fw header specifies more bytes then bytes exists in the fw file: 
	 *  kernel_len + initramfs_len + defaults_len + 
	 *   (header == 128 ? sqimage_len + 128 : 64)  > fw file size
	 * 
	 * This affects the checksum calculation, which is done on a 4 byte variable,
	 * and the fw file might not be a multiple of 4.
	 * This happens on the "defaults" fw component, which is the last one in the fw file.
	 * The following fixes the checksum calculation, making it agree with the value
	 * specified in the fw header.
	 * 
	 * However, the saved fw component does not has those extra byes.
	 * Or should it? After all the checksum and component size will only match that way
	 */

		if (n != k) {
			for (j=n; j<k; j++)
				buf[j] = 0;
			n = k;
		}

		if (write(fdo, buf, n) < 0)
			return -1;

		bp = (uint32_t *) buf;
		for (j=0; j<n/sizeof(uint32_t); j++)
			lchk ^= *bp++;   
		i += n;
	}
  
	if (*chk == 0)
		*chk = lchk;
	else if (lchk != *chk) {
		if (!quiet)
			printf("error: chksum is %lu, expected %lu\n", lchk, *chk);
		return -1;
	}

	return 0;
}

void savefile(const char *filename, int fdi, ulong offset, ulong length, uint32_t *checksum ) {

	int fdo = open(filename, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);

	if (fdo == -1) {
		if (!quiet)
			perror(filename);
		exit(1);
	}

	if (readwrite(fdo, fdi, offset, length, checksum) != 0) {
		if (!quiet)
			printf("Error on %s, exiting.\n", filename);
		exit(1);
	}
	close(fdo);

	if (!quiet)
		printf("%s saved, checksum is OK.\n", filename);
}

int is_uboot(int fd, ulong off) {
	char * file_sig[4];
	char * uboot_sig = "\x27\x05\x19\x56";

	lseek(fd, off, SEEK_SET);
	read(fd, file_sig, 4);
	if (memcmp(file_sig, uboot_sig, 4) == 0)
		return 1;
	return 0;
}

void savecomp(const char *filename, int fdo, int uboot, uint32_t *offset, uint32_t *length, uint32_t *checksum, uint32_t size_max) {

	int fdi = open(filename, O_RDONLY);
	if (fdi == -1) {
		if (!quiet)
			perror(filename);
		exit(1);
	}

	if (uboot == 1 && is_uboot(fdi, 0) == 0) {
		if (!quiet)
			printf("%s doesn't have uboot format, exiting\n", filename);
		exit(1);
	}
  
	*offset = lseek(fdo, 0, SEEK_END);
	*length = lseek(fdi, 0, SEEK_END);
	if (*length > size_max ) {
		if (!quiet)
			printf("%s size can not be more than %d bytes\n", filename, size_max);
		exit(1);
	}
  
	*checksum = 0;
	if (readwrite(fdo, fdi, 0, *length, checksum) != 0) {
		if (!quiet)
			printf("Error on %s, exiting.\n", filename);
		exit(1);
	}
	
	close(fdi);
}

void set_header64(MY_CONTROL_HEADER *myhd, CONTROL_HEADER_64 *hd) {
	hd->kernel_off = myhd->kernel_off;
	hd->kernel_len = myhd->kernel_len;
	hd->kernel_checksum = myhd->kernel_checksum;
	
	hd->initramfs_off = myhd->initramfs_off;
	hd->initramfs_len = myhd->initramfs_len;
	hd->initramfs_checksum = myhd->initramfs_checksum;
	
	hd->defaults_off = myhd->defaults_off;
	hd->defaults_len = myhd->defaults_len;
	hd->defaults_checksum = myhd->defaults_checksum;

	memcpy(&hd->magic_num, signatures[myhd->sig_num].signature, SIG_LEN);
	
	hd->product_id = myhd->product_id;
	hd->custom_id = myhd->custom_id ;
	hd->model_id = myhd->model_id;
	hd->sub_id = myhd->sub_id;
	hd->NewVersion = myhd->NewVersion;

	memset(&hd->reserved, 0, RESERVED64);
	
	hd->Next_offset = myhd->Next_offset;
}

void set_header128(MY_CONTROL_HEADER *myhd, CONTROL_HEADER_128 *hd) {	
	hd->kernel_off = myhd->kernel_off;
	hd->kernel_len = myhd->kernel_len;
	hd->kernel_checksum = myhd->kernel_checksum;
	
	hd->initramfs_off = myhd->initramfs_off;
	hd->initramfs_len = myhd->initramfs_len;
	hd->initramfs_checksum = myhd->initramfs_checksum;
	
	hd->sqimage_off = myhd->sqimage_off;
	hd->sqimage_len = myhd->sqimage_len;
	hd->sqimage_checksum = myhd->sqimage_checksum;
	
	hd->defaults_off = myhd->defaults_off;
	hd->defaults_len = myhd->defaults_len;
	hd->defaults_checksum = myhd->defaults_checksum;

	memcpy(&hd->magic_num, signatures[myhd->sig_num].signature, SIG_LEN);
	
	hd->product_id = myhd->product_id;
	hd->custom_id = myhd->custom_id ;
	hd->model_id = myhd->model_id;
	hd->sub_id = myhd->sub_id;
	hd->NewVersion = myhd->NewVersion;

	memset(&hd->reserved, 0, RESERVED128);
	
	hd->Next_offset = myhd->Next_offset;
}
	
void save_header(int fdo, MY_CONTROL_HEADER *myhd) {

	lseek(fdo, 0, SEEK_SET);
	
	if (myhd->type == 64) {
		CONTROL_HEADER_64 hd64;
		set_header64(myhd, &hd64);
		write(fdo, &hd64, sizeof(hd64));
	} else if (myhd->type == 128) {
		CONTROL_HEADER_128 hd128;
		set_header128(myhd, &hd128);
		write(fdo, &hd128, sizeof(hd128));
	} else {
		printf("Error on header type, exiting.\n");
		exit(1);
	}

  close(fdo);
}

/* some fw files have incorrect default-settings size
 * -this leads to the sum of the fw components, plus the file header,
 *  to be greater then the file size
 * -as the default-settings component use to be the last component,
 *  its size extends past the file end
 * However, since the computed checksums of each component are correct,
 * this file size check does not seems to be needed.
 */
int size_ok(int fd, MY_CONTROL_HEADER * hd) {
	ulong fsize = lseek(fd, 0, SEEK_END);
		
	return 1;

	if (hd->kernel_len + hd->initramfs_len + hd->defaults_len + 
		(hd->type == 128 ? hd->sqimage_len + 128 : 64)  > fsize ||
		hd->kernel_off + hd->kernel_len > fsize ||
		hd->initramfs_off + hd->initramfs_len > fsize ||
		hd->defaults_off + hd->defaults_len > fsize ||
		(hd->type == 128 && hd->sqimage_off + hd->sqimage_len > fsize))
		return 0;
	return 1;
}

void get_info64(CONTROL_HEADER_64 * hd, MY_CONTROL_HEADER * myhd) {
	myhd->product_id = hd->product_id;
	myhd->custom_id = hd->custom_id;
	myhd->model_id = hd->model_id;
	myhd->sub_id = hd->sub_id;
	myhd->NewVersion = hd->NewVersion;
	myhd->type = 64;
	
	myhd->kernel_off = hd->kernel_off;
	myhd->kernel_len = hd->kernel_len;
	myhd->kernel_checksum = hd->kernel_checksum;
	
	myhd->initramfs_off = hd->initramfs_off;
	myhd->initramfs_len = hd->initramfs_len;
	myhd->initramfs_checksum = hd->initramfs_checksum;

	myhd->defaults_off = hd->defaults_off;
	myhd->defaults_len = hd->defaults_len;
	myhd->defaults_checksum = hd->defaults_checksum;

	myhd->Next_offset = hd->Next_offset;
}

void get_info128(CONTROL_HEADER_128 * hd, MY_CONTROL_HEADER * myhd) {
	myhd->product_id = hd->product_id;
	myhd->custom_id = hd->custom_id;
	myhd->model_id = hd->model_id;
	myhd->sub_id = hd->sub_id;
	myhd->NewVersion = hd->NewVersion;
	myhd->type = 128;
	
	myhd->kernel_off = hd->kernel_off;
	myhd->kernel_len = hd->kernel_len;
	myhd->kernel_checksum = hd->kernel_checksum;
	
	myhd->initramfs_off = hd->initramfs_off;
	myhd->initramfs_len = hd->initramfs_len;
	myhd->initramfs_checksum = hd->initramfs_checksum;
	
	myhd->sqimage_off = hd->sqimage_off;
	myhd->sqimage_len = hd->sqimage_len;
	myhd->sqimage_checksum = hd->sqimage_checksum;
	
	myhd->defaults_off = hd->defaults_off;
	myhd->defaults_len = hd->defaults_len;
	myhd->defaults_checksum = hd->defaults_checksum;
	
	myhd->Next_offset = hd->Next_offset;
}

int cmp_sig(uchar * t) {
	int i;
	
	for(i=0; i<nsig; i++) {
		if (memcmp(signatures[i].signature, t, SIG_LEN) == 0)
			return signatures[i].idx;
	}
	return -1;
}

int check_sig(uchar * hd, MY_CONTROL_HEADER * myhd) {
	int t;
	
	CONTROL_HEADER_64 * hd64 = (CONTROL_HEADER_64 *) hd;
	CONTROL_HEADER_128 * hd128 = (CONTROL_HEADER_128 *) hd;
	
	if ((t = cmp_sig(hd64->magic_num)) != -1) {
		get_info64(hd64, myhd);
		myhd->sig_num = t;
		return t;
	}

	if (( t = cmp_sig(hd128->magic_num)) != -1) {
		get_info128(hd128, myhd);
		myhd->sig_num = t;
		return t;
	}
	return -1;
}

void print_info(int fd, MY_CONTROL_HEADER *hd) {	
	printf("product_id=%x;\ncustom_id=%x;\nmodel_id=%x;\nsub_id=%x;\nNewVersion=%x;\nsignature=\"%.8s\";\n",
		hd->product_id, hd->custom_id, hd->model_id, hd->sub_id,
		hd->NewVersion, signatures[hd->sig_num].signature+2);

	if (!quiet)
		printf("\nsig_num=%d header=%d Next_offset=%lu\n",
			hd->sig_num, hd->type, hd->Next_offset);
	
	if (!quiet) {
		ulong ko, kl, kc, io, il, ic, qo, ql, qc, so, sl, sc;
		int kr, ir, qr, sr;
		
		ko = hd->kernel_off; kl = hd->kernel_len; kc = hd->kernel_checksum; kr = hd->kernel_len % 4;
		io = hd->initramfs_off; il = hd->initramfs_len; ic = hd->initramfs_checksum; ir = hd->initramfs_len % 4;
		qo = hd->sqimage_off; ql = hd->sqimage_len; qc = hd->sqimage_checksum; qr = hd->sqimage_len % 4;
		so = hd->defaults_off; sl = hd->defaults_len; sc = hd->defaults_checksum; sr = hd->defaults_len % 4;

		printf("ko=%lu\t\tkl=%lu\tkr=%d\tkc=%lu\tnext=%lu\n", ko, kl, kr, kc, ko+kl);
		printf("io=%lu\til=%lu\tir=%d\tic=%lu\tnext=%lu\n", io, il, ir, ic, io+il);
		if (hd->type == 128)
			printf("so=%lu\tsl=%lu\tsr=%d\tsc=%lu\tnext=%lu\n", qo, ql, qr, qc, qo+ql);
		printf("do=%lu\tdl=%lu\t\tdr=%d\tdc=%lu\tnext=%lu\n", so, sl, sr, sc, so+sl);

		printf("filesz=%lu compsz=%lu\n",
			lseek(fd, 0, SEEK_END), kl + il + sl + (hd->type == 128 ? ql + 128 : 64));
	}
	
	if (!quiet && hd->Next_offset != 0) {
		EXTEND_HEADER ehd;
		lseek(fd, hd->Next_offset, SEEK_SET);
		read(fd, &ehd, sizeof(ehd));
		printf("Next header at %lu: dir=%.32s file=%.32s\n\toff=%lu len=%lu checksum=%lu next_offset=%lu\n",
			   hd->Next_offset, ehd.Directory, ehd.FileName, ehd.offset, ehd.len, ehd.checksum, ehd.Next_offset);
	}
}

void usage() {
	fprintf(stderr, "-Split a vendor firmware file into its components:\n"
		"\tdns323-fw -s [-q (quiet)]\n"
		"\t[-k kernel_file] [-i initramfs_file] [-a sqimage_file] [-d defaults_file] firmware_file\n");
		
	fprintf(stderr, "-Merge a kernel and initramfs into a firmware compatible vendor firmware file:\n"
		"\tdns323-fw -m [-q (quiet)]\n"
		"\t-k kernel_file -i initramfs_file [-a sqimage_file] [-d defaults_file]\n"
		"\t[-p product_id]  [-c custom_id] [-l model_id ] [-u sub_id] [-v new_version]\n"
		"\t[-t type (0-FrodoII, 1-Chopper, 2-Gandolf, 3-DNS-325-A1A2, 4-DNS-320-A1A2, 5-DNS-320-B 6-DNS-320L, 7-DNS-327L] firmware_file\n");
  
	fprintf(stderr, "-Print information from a firmware file:\n"
		"\tdns323-fw -f firmware_file\n");
  
	exit(1);
}

int merge() {
	MY_CONTROL_HEADER myhd;

	if (kernel == NULL || initramfs == NULL || fw == NULL)
		usage();

	if (type >= nsig)
		usage();

	//if (signatures[type].size == 128 && sqimage == NULL)
	//	  usage();

	int hd_size = signatures[type].size;
	myhd.sig_num = type;
	myhd.type = hd_size;

	int fdo = open(fw, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU); // output file
	if (fdo == -1) {
		perror(fw);
		exit(1);
	}

	// kernel
	write(fdo, &myhd, hd_size); /* fake write, updated at the end */
	savecomp(kernel, fdo, 1,
		&myhd.kernel_off, &myhd.kernel_len,
		&myhd.kernel_checksum, signatures[type].kernel_max);

	// initramfs 
	savecomp(initramfs, fdo, 1,
		&myhd.initramfs_off, &myhd.initramfs_len,
		&myhd.initramfs_checksum, signatures[type].initramfs_max);

  // sqimage
	if (hd_size == 128) {
		if (sqimage != NULL) {
			savecomp(sqimage, fdo, 0,
				&myhd.sqimage_off, &myhd.sqimage_len,
				&myhd.sqimage_checksum, signatures[type].sqimage_max);
		} else {
			myhd.sqimage_off = lseek(fdo, 0, SEEK_END);  
			myhd.sqimage_len = 0;
			myhd.sqimage_checksum = 0;
		}
	}
  
	// default
	if (defaults != NULL) {
		savecomp(defaults, fdo, 0,
			&myhd.defaults_off, &myhd.defaults_len,
			&myhd.defaults_checksum, signatures[type].defaults_max);
	} else {
		myhd.defaults_off = lseek(fdo, 0, SEEK_END);  
		myhd.defaults_len = 0;
		myhd.defaults_checksum = 0;
	}

	myhd.product_id = product;
	myhd.custom_id = custom;
	myhd.model_id = model;
	myhd.sub_id = sub;
	myhd.NewVersion = version;
	myhd.Next_offset = 0;

	save_header(fdo, &myhd);

	if (!quiet) {
		printf("product_id=%x\ncustom_id=%x\nmodel_id=%x\nsub_id=%x\nNewVersion=%x\ntype=%x\n",
			myhd.product_id, myhd.custom_id, myhd.model_id, myhd.sub_id, myhd.NewVersion, myhd.sig_num);

		printf("signature is \"%.8s\"\n", signatures[myhd.sig_num].signature+2);
		printf("kernel has %lu bytes\n", myhd.kernel_len);
		printf("initramfs has %lu bytes\n", myhd.initramfs_len);
		if (myhd.type == 128)
			printf("sqimage has %lu bytes\n", myhd.sqimage_len);
		printf("defaults has %lu bytes\n", myhd.defaults_len);
	}
	return 0;
}

int open_read(MY_CONTROL_HEADER *myhd) {
	uchar hd[sizeof(CONTROL_HEADER_128)];
	
	int fd = open(fw, O_RDONLY);
	if (fd < 0) {
		perror(fw);
		exit(1);
	}

	if (read(fd, hd, sizeof(CONTROL_HEADER_128)) !=  sizeof(CONTROL_HEADER_128)) {
		perror("reading file");
		exit(1);
	}
 
	if ((type = check_sig(hd, myhd)) == 255) { /* FIXME: type is uchar, check_sig returns -1 on error */
		if (!quiet)
			printf("Signature does not match known signatures, exiting.\n");
		exit(1);
	}
	print_info(fd, myhd);

	return fd;
}

int info() {
	MY_CONTROL_HEADER myhd;

	if (fw == NULL)
		usage();

	int fd = open_read(&myhd);

	return close(fd);
}

int split() {
	MY_CONTROL_HEADER myhd;

	if (kernel == NULL)
		kernel = "kernel";
	if (initramfs == NULL)
		initramfs = "initramfs";
	if(sqimage == NULL)
		sqimage = "sqimage";
	if (defaults == NULL)
		defaults = "defaults";

	if (fw == NULL)
		usage();

	int fd = open_read(&myhd);

	if ( myhd.Next_offset != 0) {
		if (!quiet)
			printf("\nWARNING, this firmware has unknown components.\n");
	}

	if (!quiet)
		printf("\n");

	if (size_ok(fd, &myhd) == 0) {
		if (!quiet)
			printf("File has insuficient size for its header specification, exiting.\n");
		exit(1);
	}

	if (!quiet)
		printf("signature is \"%.8s\"\n", signatures[type].signature+2);

	if (is_uboot(fd, myhd.kernel_off) == 0 || is_uboot(fd, myhd.initramfs_off) == 0) {
		if (!quiet)
			printf("kernel or initramfs firmware components doesn't have uboot format, exiting.\n");
		exit(1);
	}

	savefile(kernel, fd, myhd.kernel_off, myhd.kernel_len, &myhd.kernel_checksum );
	savefile(initramfs, fd, myhd.initramfs_off, myhd.initramfs_len, &myhd.initramfs_checksum);

	if (myhd.type == 128)
		savefile(sqimage, fd, myhd.sqimage_off, myhd.sqimage_len, &myhd.sqimage_checksum);

	savefile(defaults, fd, myhd.defaults_off, myhd.defaults_len, &myhd.defaults_checksum);

	close(fd);
	return 0;
}

int main(int argc, char *argv[]) {
	typedef enum {NONE, SPLIT, MERGE, INFO} Oper;
	Oper op = NONE;
	int opt;

	while ((opt = getopt(argc, argv, "smfqk:i:d:p:c:a:l:u:v:t:")) != -1) {
		switch (opt) {
		case 's': op = SPLIT; break;
		case 'm': op = MERGE; break;
		case 'f': op = INFO; break;
		case 'q': quiet = 1; break;
		case 'k': kernel = optarg; break;
		case 'i': initramfs = optarg; break;
		case 'a': sqimage = optarg; break;
		case 'd': defaults = optarg; break;
		case 'p': product = atoi(optarg); break;
		case 'c': custom = atoi(optarg); break;
		case 'l': model = atoi(optarg); break;
		case 'u': sub = atoi(optarg); break;		
		case 'v': version = atoi(optarg); break;
		case 't': type = atoi(optarg); break;
		default: /* '?' */usage();
		}
	}
		
	if (optind >= argc)
		usage();
	else
		fw = argv[optind];

	switch(op) {
		case SPLIT: return split();
		case MERGE: return merge();
		case INFO: return info();
		default: usage();
	}

	return 1;	
}
