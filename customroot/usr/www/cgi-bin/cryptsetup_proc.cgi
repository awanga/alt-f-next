#!/bin/sh

. common.sh

check_cookie
read_args

#debug

CONFF=/etc/misc.conf

. $CONFF

sed -i '/^MODLOAD_CESA=/d' $CONFF >& /dev/null
if test -z "$use_cesa"; then
	rmmod mv_cesa >& /dev/null
else
	modprobe -q mv_cesa  >& /dev/null
	echo MODLOAD_CESA=y >> $CONFF
fi

sed -i '/^CRYPT_KEYFILE=/d' $CONFF >& /dev/null
if test -n "$keyfile"; then
	echo "CRYPT_KEYFILE=$(httpd -d $keyfile)" >> $CONFF
fi

if test "$action" = "Format"; then
	if ! test -f "$CRYPT_KEYFILE" -a -b "/dev/$devto"; then
		msg "Password file $CRYPT_KEYFILE or device /dev/$devto does not exist."
	fi

	# is a normal partition mounted?	
	if grep -q ^/dev/$devto /proc/mounts; then
		if ! umount /dev/$devto >& /dev/null; then
			msg "Device $devto is currently mounted and couldn't be unmounted, stop services first."
		fi
		(cd /dev && ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$devto /usr/sbin/hot.sh)
	fi

	dm=${devto}-crypt
	if test -b /dev/mapper/$dm; then
		# find device-mapper name under /dev, e.g. /dev/dm-3
		eval $(dmsetup ls | awk '/'$dm'/{printf "mj=%d mi=%d", substr($2,2), $3}')
		eval $(awk '/'$mj' *'$mi'/{printf "tdm=%s", $4}' /proc/partitions)

		(cd /dev && ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$tdm /usr/sbin/hot.sh)
		if test $? != 0; then
			msg "Device $tdm is currently mounted and couldn't be unmounted, stop services first."
		fi

		if ! cryptsetup luksClose $dm >& /dev/null; then
			msg "Device $dm is already an encrypted device but couldn't be deactivated."
		fi
	fi

	res="$(cryptsetup -q --cipher="$(httpd -d $cipher)" --key-size=$nbits luksFormat --key-file=$CRYPT_KEYFILE /dev/$devto 2>&1)"
	if test $? != 0; then
		msg "$res"
	fi
elif test -n "$Open"; then
	dsk=$Open
	cryptsetup --key-file=$CRYPT_KEYFILE luksOpen /dev/$dsk ${dsk}-crypt

elif test -n "$Close"; then
	dsk=$Close
	dm=${dsk}-crypt
	
	# find device-mapper name under /dev, e.g. /dev/dm-3 
	eval $(dmsetup ls | awk '/'$dm'/{printf "mj=%d mi=%d", substr($2,2), $3}')
	eval $(awk '/'$mj' *'$mi'/{printf "tdm=%s", $4}' /proc/partitions)

	(cd /dev && ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$tdm /usr/sbin/hot.sh)
	cryptsetup --key-file=$CRYPT_KEYFILE luksClose $dm
fi

#enddebug
gotopage /cgi-bin/cryptsetup.cgi
