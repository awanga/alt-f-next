/*
 * Copyright Joao Cardoso 2009
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

	unsigned char magic_num[12];
	unsigned char product_id;
	unsigned char custom_id;
	unsigned char model_id;
	unsigned char sub_id;

	unsigned char NewVersion;
	unsigned char reserved[7];	//all structure is 64 bytes
	uint32_t Next_offset;
} CONTROL_HEADER;

typedef unsigned long ulong;
typedef unsigned char uchar;

unsigned char *signatures[] = { 
	"\x55\xAA" "FrodoII" "\x00\x55\xAA", 
	"\x55\xAA" "Chopper" "\x00\x55\xAA",
	"\x55\xAA" "Gandolf" "\x00\x55\xAA"
};

#define BLOCK_SIZE	0x10000

// cat /proc/mtd
#define MTD_DEFLT	0x00010000
#define MTD2_KERNEL	0x00180000
#define MTD3_FSYS	0x00630000

char *kernel = NULL, *initramfs = NULL, *defaults = NULL, *fw = NULL;
unsigned char product = 1, custom = 2, model = 3, sub = 4, version = 5, type = 0, quiet = 0;

int readwrite(int fdo, int fdi, ulong off, ulong sz, uint32_t *chk) {

  char *buf = (char *) malloc(BLOCK_SIZE);
  if (buf == NULL) {
	perror("malloc");
	return -1;
  }

  if (lseek(fdi, off, SEEK_SET) < 0)
	return -1;

  int i, j, n;
  uint32_t lchk = 0;
  uint32_t *bp;
  for (i=0; i<sz/BLOCK_SIZE; i++) {
	n = read(fdi, buf, BLOCK_SIZE);
	if (n < 0)
	  return -1;
	if (write(fdo, buf, n) < 0)
	  return -1;
	bp = (uint32_t *) buf;
	for (j=0; j<n/sizeof(uint32_t); j++)
	  lchk ^= *bp++; 
  }

  n = read(fdi, buf, sz - i*BLOCK_SIZE);
  if (n < 0)
	return -1;
  if (write(fdo, buf, n) < 0)
	return -1;
  bp = (uint32_t *) buf;
  for (j=0; j<n/sizeof(uint32_t); j++)
	lchk ^= *bp++; 

  free(buf);

  if (*chk == 0)
	*chk = lchk;
  else 	if (lchk != *chk) {
	if (!quiet) printf("chksum=%lu expected %lu\n", lchk, *chk);
	return -1;
  }

  return 0;
}

int is_uboot(int fd, ulong off) {
  char * file_sig[4];
  char * uboot_sig = "\x27\x05\x19\x56";

  lseek(fd, off, SEEK_SET);
  read(fd, file_sig, 4);
  if (memcmp(file_sig, uboot_sig, 4) == 0) {
	return 1;
  }
  return 0;
}

int check_sig(CONTROL_HEADER * hd) {
  int i;
  for(i=0; i<3; i++) {
	if (memcmp(signatures[i], hd->magic_num, 12) == 0) {
	  return i;
	}
  }
  return -1;
}

int size_ok(int fd, CONTROL_HEADER * hd) {
  ulong fsize = lseek(fd, 0, SEEK_END);
  if ( hd->kernel_off + hd->kernel_len > fsize ||
	   hd->initramfs_off + hd->initramfs_len > fsize ||
	   hd->defaults_off + hd->defaults_len > fsize ) {
	return 0;
  }
  return 1;
}

void usage() {
  fprintf(stderr, "Split a vendor firmware file into its components:\n"
		  "\tdns323-fw -s [-q (quiet)] [-k kernel_file] [-i initramfs_file]\n"
		  "\t[-d defaults_file] firmware_file\n");
		
  fprintf(stderr, "Merge a kernel and initramfs into a firmware compatible vendor firmware file:\n"
		  "\tdns323-fw -m [-q (quiet)] -k kernel_file -i initramfs_file [-d defaults_file]\n"
		  "\t[-p product_id]  [-c custom_id] [-l model_id ] [-u sub_id] [-v new_version]\n"
		  "\t[-t type (0-FrodoII, 1-Chopper, 2-Gandolf] firmware_file\n");
  exit(1);
}
			
int merge() {
  CONTROL_HEADER hd;
 
  if (kernel == NULL || initramfs == NULL || fw == NULL)
	usage();
 
  int fo = open(fw, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU); // output file
  if (fo == -1) {
	perror(fw);
	exit(1);
  }

  // kernel
  int fi = open(kernel, O_RDONLY); 
  if (fi < 0) {
	perror(kernel);
	exit(1);
  }
 
  if (is_uboot(fi, 0) == 0) {
	if (!quiet) printf("kernel doesn't have uboot format, exiting\n");
	exit(1);
  }

  ulong fsize = lseek(fi, 0, SEEK_END);
  if (fsize > MTD2_KERNEL ) {
	if (!quiet) printf("Kernel sizes can not be more than %d bytes\n", MTD2_KERNEL);
	exit(1);
  }
    
  lseek(fo, 64, SEEK_SET);
  uint32_t chks = 0;
  if (readwrite(fo, fi, 0, fsize, &chks) != 0) {
	perror("readwrite kernel");
	exit(1);
  }

  close(fi);

  hd.kernel_off = 64;
  hd.kernel_len = fsize;
  hd.kernel_checksum = chks;

  // initramfs
  fi = open(initramfs, O_RDONLY);
  if (fi < 0) {
	perror(initramfs);
	exit(1);
  }

  if (is_uboot(fi, 0) == 0) {
	if (!quiet) printf("initramfs doesn't have uboot format, exiting\n");
	exit(1);
  }

  fsize = lseek(fi, 0, SEEK_END);
  if (fsize > MTD3_FSYS) {
	if (!quiet) printf("initramfs size can not be more than %d bytes\n", MTD3_FSYS );
	exit(1);
  }

  chks = 0;
  if (readwrite(fo, fi, 0, fsize, &chks) != 0) {
	perror("readwrite initramfs");
	exit(1);
  }

  close(fi);

  hd.initramfs_off = hd.kernel_off + hd.kernel_len ;
  hd.initramfs_len = fsize;
  hd.initramfs_checksum = chks;

  // default
  if (defaults != NULL) {
	fi = open(defaults, O_RDONLY); 
	if (fi < 0) {
	  perror("read defaults");
	  exit(1);
	}

	fsize = lseek(fi, 0, SEEK_END);
	if (fsize > MTD_DEFLT ) {
	  if (!quiet) printf("default size can not more than %d bytes\n", MTD_DEFLT);
	  exit(1);
	}

	chks = 0;
	if (readwrite(fo, fi, 0, fsize, &chks) != 0) {
	  perror("readwrite defaults");
	  exit(1);
	}

	close(fi);
  } else {
	chks = 0;
	fsize = 0;
  }

  hd.defaults_off = hd.kernel_off + hd.kernel_len + hd.initramfs_len;
  hd.defaults_len = fsize;
  hd.defaults_checksum = chks;

  memcpy(&hd.magic_num, signatures[type], 12);
  hd.product_id = product;
  hd.custom_id = custom;
  hd.model_id = model;
  hd.sub_id = sub;
  hd.NewVersion = version;
  memset(&hd.reserved, 0, 7);
  hd.Next_offset = 0;

  lseek(fo, 0, SEEK_SET);
  write(fo, &hd, sizeof(hd));
  close(fo);

  if (!quiet) { 
	printf("product_id=%x\ncustom_id=%x\nmodel_id=%x\nsub_id=%x\nNewVersion=%x\ntype=%x\n",
		 hd.product_id, hd.custom_id, hd.model_id, hd.sub_id, hd.NewVersion, type);
	printf("signature is \"%s\n", hd.magic_num+2);
	printf("kernel has %lu bytes\n", hd.kernel_len);
	printf("initramfs has %lu bytes\n", hd.initramfs_len);
	printf("defaults has %lu bytes\n", hd.defaults_len);
  }
  return 0;
}

int split() {
  CONTROL_HEADER hd;
  int i;
 
  if (kernel == NULL)
	kernel = "kernel";
  if (initramfs == NULL)
	initramfs = "initramfs";
  if (defaults == NULL)
	defaults = "defaults";

  if (fw == NULL)
	usage();

  int fd = open(fw, O_RDONLY);
  if (fd < 0) {
	perror(fw);
	exit(1);
  }

  if (read(fd, &hd, sizeof(CONTROL_HEADER)) !=  sizeof(CONTROL_HEADER)) {
	perror("reading file");
	exit(1);
  }
 
  type = check_sig(& hd);
  
  printf("product_id=%x;\ncustom_id=%x;\nmodel_id=%x;\nsub_id=%x;\nNewVersion=%x;\ntype=%x;\n",
		 hd.product_id, hd.custom_id, hd.model_id, hd.sub_id, hd.NewVersion, type);

  if (!quiet) {
	printf("Reserved (hex)=");
	for (i=0; i<7; i++)
	  printf("%x", hd.reserved[i]);
	printf("\nReserved (ascii)=");
	for (i=0; i<7; i++)
	  printf("%c", hd.reserved[i]);
	printf("\nNext_offset=%lu\n", hd.Next_offset);
  }

  if ( hd.Next_offset != 0) {
	if (!quiet) printf("\nWARNING, this firmware has more components then just a kernel,"
		   "a initramfs and a defaults file. Exiting now.\n");
	exit(1);
  }

  if (!quiet)  printf("\n");

  if (size_ok(fd, &hd) == 0) {
	if (!quiet) printf("File has insuficient size for its header specification, exiting\n");
	exit(1);
  }

  if (type == -1) {
	if (!quiet) printf("Signature does not match known signatures, exiting\n");
	exit(1);
  } else
	if (!quiet) printf("signature is \"%s\"\n", signatures[type]+2);

  if (is_uboot(fd, hd.kernel_off) == 0) {
	if (!quiet) printf("kernel doesn't have uboot format, exiting\n");
	exit(1);
  }

  int fo = open(kernel, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);
  if (fo == -1) {
	if (!quiet) perror(kernel);
	exit(1);
  }

  if (readwrite(fo, fd, hd.kernel_off, hd.kernel_len, &hd.kernel_checksum) != 0) {
	if (!quiet) printf("Error on kernel, exiting.\n");
	exit(1);
  }
  close(fo);

  if (!quiet)  printf("kernel has uboot format\nkernel checksum OK\n"
		 "kernel has %lu bytes\nkernel saved OK\n", hd.kernel_len);

  if (is_uboot(fd, hd.initramfs_off) == 0) {
	if (!quiet) printf("initramfs doesn't have uboot format, exiting\n");
	exit(1);
  }
 
  fo = open(initramfs, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);
  if (fo == -1) {
	if (!quiet) perror(initramfs);
	exit(1);
  }

  if (readwrite(fo, fd, hd.initramfs_off, hd.initramfs_len, &hd.initramfs_checksum) != 0) {
	if (!quiet) printf("Error on initramfs, exiting.\n");
	exit(1);
  }
  close(fo);
  if (!quiet) printf("initramfs has uboot format\ninitramfs checksum OK\n"
		 "initramfs has %lu bytes\ninitramfs saved OK\n", hd.initramfs_len);

  fo = open(defaults, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);
  if (fo == -1) {
	if (!quiet) perror(defaults);
	exit(1);
  }

  if (readwrite(fo, fd, hd.defaults_off, hd.defaults_len, &hd.defaults_checksum) != 0) {
	if (!quiet) printf("Error on defaults, exiting\n");
	exit(1);
  }
  close(fo);
  if (!quiet) printf("defaults checksum OK\ndefaults has %lu bytes\ndefaults saved OK\n", hd.defaults_len);

  close(fd);
  return 0;
}

int main(int argc, char *argv[]) {
  typedef enum {NONE, SPLIT, MERGE} Oper;
  Oper op = NONE;
  int opt;
  
  while ((opt = getopt(argc, argv, "smqk:i:d:p:c:l:u:v:t:")) != -1) {
	switch (opt) {
	case 's': op = SPLIT; break;
	case 'm': op = MERGE; break;
	case 'q': quiet = 1; break;
	case 'k': kernel = optarg; break;
	case 'i': initramfs = optarg; break;
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
	
  if (op == SPLIT)
	return split();
  else if (op == MERGE)
	return merge();
  else
	usage();
	
  return 1;	
}

