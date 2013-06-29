#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFM=/etc/misc.conf
CONFFSTAB=/etc/fstab

# lumount part msg
lumount() {
	if ismount $1; then
		cd /dev
		ACTION=remove DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
		if test $? != 0; then
			msg "Couldn't unmount /dev/$1 for $2 it, stop services first."
		fi
	fi
}

# lmount part msg
lmount() {
	if ! ismount $1; then
		if isdirty $part; then
			msg "Filesystem $part is dirty, check it before mounting."
		fi

		cd /dev
		ACTION=add DEVTYPE=partition PWD=/dev MDEV=$1 /usr/sbin/hot.sh
		if test $? != 0; then
			msg "Couldn't mount /dev/$1 for $2 it."
		fi
	fi
}

# $1-part $2-mopts
remount() {
	part=$1
	mopts=$2

	lumount "$part"

	TF=$(mktemp -t) 
	awk '{
		if ($1 == "/dev/'$part'") {
			$4 = "'$mopts'"
			printf "%s\n", $0
		} else {
			print $0
		}
	}' $CONFFSTAB > $TF
	mv $TF $CONFFSTAB

	uuid=$(blkid -o value -c /dev/null -s UUID /dev/$part | tr '-' '_')
	sed -i '/^mopts_'${uuid}'=/d' $CONFM

	if test "$mopts" != "defaults"; then
		echo "mopts_${uuid}=$mopts" >> $CONFM
	fi
	
	lmount "$part"
}

h2b() {
	v=$1
	l=$((${#v}-1))
	s=${v:$l}
	if echo "$s" | grep -qE '(K|k|M|m|G|g|T|t)'; then
		v=${v:0:$l}
		case "$s" in
			t|T) m=$((1024 * 1024 * 1024)) ;;
			g|G) m=$((1024 * 1024)) ;;
			m|M) m=1024 ;;
			k|K) m=1 ;;
		esac
		v=$((v * m))
	fi
	echo $v
}

if test -n "$Report"; then
	html_header "Quota Report"
	echo "<pre>"
	repquota -ugsa | sed -e 's|.*Report.*|<h4>&</h4>|' -e 's|.*+.*|<span style="color:red">&</span>|'
	echo "</pre>$(back_button)</body></html>"
	exit 0

elif test -n "$CheckNow"; then
	part=$CheckNow
	if ! lbl=$(plabel /dev/$part); then lbl=$part; fi
	if ! test -f /mnt/$lbl/aquota.group -a -f /mnt/$lbl/aquota.user; then
		opt="-c"
	fi
	quotaoff -ug /dev/$part >& /dev/null
	quotacheck -ugv $opt /dev/$part >& /dev/null
	quotaon -ug /dev/$part >& /dev/null

elif test -n "$quota_global"; then
	quota_mopts='jqfmt=vfsv0,usrjquota=aquota.user,grpjquota=aquota.group'
	fsl=$(grep -E '(ext2|ext3|ext4)' /proc/mounts | cut -d" " -f1)

	for i in $(seq 0 $glb_cnt); do
		enable=$(eval echo \$enable_$i)
		if test -n "$enable"; then
			fs=$enable
			fsl=$(echo $fsl | sed "s|/dev/$fs||") # fs processed, remove from list

			if ! grep -q "^/dev/$fs.*$quota_mopts" /proc/mounts; then # is not enabled
				mopts="$(awk '{ if ($1 == "/dev/'$fs'") print $4}' $CONFFSTAB),$quota_mopts"
				remount $fs $mopts
				sleep 1 # mount is asynchronous, give it some tolerance
			fi

			active=$(eval echo \$active_$i)
			if test -n "$active"; then
				if quotaon -p /dev/$fs >& /dev/null; then
					res=$(quotaon -ug /dev/$fs 2>&1 )
					if test "$?" != 0; then
						if ! lbl=$(plabel $fs); then lbl="$fs"; fi
						if ! test -f /mnt/$lbl/aquota.user -a -f /mnt/$lbl/aquota.group; then
							msg "Before activating quotas for the first time on $lbl,
you have to use the CheckNow button first."
						else
							msg "$res"
						fi
					fi
				fi
			else
				quotaoff -ug /dev/$fs >& /dev/null
			fi
		fi
	done

	# process disabled fs
	for i in $fsl; do
		if grep -q "^$i.*$quota_mopts" /proc/mounts; then # is enabled, disable
			quotaoff -ug $i >& /dev/null
			mopts=$(awk '{ if ($1 == "'$i'") print $4}' $CONFFSTAB | sed 's/,'$quota_mopts'//')
			remount $(basename $i) $mopts
		fi
	done

elif test -n "$quota_user"; then
	for i in $(seq 1 12); do
		fs=$(eval echo \$fs_$i)
		if test -z "$fs"; then break; fi
		bquota=$(h2b $(eval echo \$bquota_$i))
		blimit=$(h2b $(eval echo \$blimit_$i))
		fquota=$(eval echo \$fquota_$i)
		flimit=$(eval echo \$flimit_$i)
		res=$(setquota $opt $targ $bquota $blimit $fquota $flimit /dev/$fs 2>&1)
		if test "$?" != 0; then msg "$res"; fi
	done
fi

#enddebug
gotopage /cgi-bin/quota.cgi?$kind=$targ
