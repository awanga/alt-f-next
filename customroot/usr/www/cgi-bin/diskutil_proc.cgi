#!/bin/sh

# $1=HDSLEEP_* | HDPOWER_* $2=val
prog() {
	local dsk tmout
	dsk=$(grep -i ${1#*_}_dev /etc/bay | cut -d"=" -f2)
	act=${1%_*}
	op="$2"

	if test -z "$dsk" -o ! -b /dev/$dsk; then
		return
	fi

	case $act in
		HDSLEEP)
			if test "$op" -eq "0"; then
				tmout=0;
			elif test "$op" -le "20"; then
				tmout=$((op * 60 / 5));
			elif test "$op" -le "300"; then
				tmout=$((240 + op / 30));
			fi
			hdparm -S $tmout /dev/$dsk >& /dev/null
			;;
		HDPOWER)
			hdparm -B $op /dev/$dsk >& /dev/null
			;;
	esac
}

health() {
	local dsk
	dsk=/dev/$1

	if ! test -b $dsk; then
		return
	fi

	res=$(smartctl -H -i -A -l error -l selftest $dsk)
	html_header
	echo "<pre><small>"
	echo "$res"
	echo  "</small></pre>$(back_button)</html></body>"
}

# $1=dsk $2=op
bay_eject() {
	local bay dsk eop
	dsk=$1
	if test $# = 2; then
		eop=$2
	fi

	disk_details $1

	eject $eop $dsk >/dev/null
	if test -z "$eop" -a $? = 0; then
		msg "You can now physically remove the $dbay device"
	elif test -z "$eop" -a $? != 0; then
		msg "Eject failed, some programs are using the $dbay device"
	else
		msg "Filesystems on $dbay disk mounted"
	fi
}

. common.sh

check_cookie
read_args
		    
#debug

CONFT=/etc/misc.conf
FSTAB=/etc/fstab
SYSCTL_CONF=/etc/sysctl.conf
SWAPP=/proc/swaps

if test "$action" = "smart_act"; then
	if test -n "$hstatus"; then
		health $hstatus
		exit

	elif test -n "$shorttest"; then
		if res=$(smartctl -t short /dev/$shorttest); then
			res=$(echo $res | sed -n 's/.*successful\.\(.*\)Use.*/\1/p')
			msg "$res\n\nYou can see the result using Health Status."
		else
			msg "Fail: $res"
		fi

	elif test -n "$longtest"; then
		if res=$(smartctl -t long /dev/$longtest); then
			res=$(echo $res | sed -n 's/.*successful\.\(.*\)Use.*/\1/p')
			hdparm -S 0 /dev/$longtest >& /dev/null
			msg "$res\n\nYou can see the result using Health Status.\n\nDisk spindown has been disabled,\nyou have to reenable it after the test completes."
		else
			msg "Fail: $res"
		fi
	fi

elif test "$action" = "swap_act"; then
	for i in $(seq 1 $count); do
		swap_dev=$(eval echo \$swapd_$i)
		swap_pri=$(eval echo \$swapp_$i)

		cur_pri=$(awk '/\/dev\/'$swap_dev'/{print $5}' $SWAPP)
		if test "$cur_pri" = "$swap_pri"; then continue; fi

		swapoff /dev/$swap_dev >& /dev/null
		eval $(blkid /dev/$swap_dev | cut -d" " -f3 | tr '-' '_')

		if test -z "$UUID" -o "$swap_pri" != "0"; then
			if test -z "$UUID" || ! blkid -t TYPE=swap /dev/$swap_dev >&/dev/null; then
				mkswap /dev/$swap_dev >& /dev/null
				eval $(blkid /dev/$swap_dev | cut -d" " -f3 | tr '-' '_')
			fi
			if ! res=$(swapon -p $swap_pri /dev/$swap_dev 2>&1); then msg "$res"; fi
		fi
		sed -i "/swapp_$UUID/d" $CONFT
		echo "swapp_$UUID=$swap_pri" >> $CONFT

		touch -r $FSTAB /tmp/fstab_date
		sed -i '\|^/dev/'$swap_dev'|d' $FSTAB
		echo "/dev/$swap_dev none swap pri=$swap_pri 0 0" >> $FSTAB
		touch -r /tmp/fstab_date $FSTAB
		rm -f /tmp/fstab_date
	done

elif test "$action" = "power_act"; then
	if test -n "$standby" -o -n "$HDPOWER_LEFT" -o -n "$HDPOWER_RIGHT" -o -n "$HDPOWER_USB"; then
		for i in HDPOWER_LEFT HDPOWER_RIGHT HDPOWER_USB HDSLEEP_LEFT HDSLEEP_RIGHT HDSLEEP_USB; do
			if test -n "$(eval echo \$$i)"; then
				sed -i '/^'$i'/d' $CONFT >& /dev/null
				echo "$i=$(eval echo \$$i)" >> $CONFT
				prog $i $(eval echo \$$i)
			fi
		done
	fi

elif test "$action" = "swappiness_act"; then
	if test "$swappiness" -ge 0 -a "$swappiness" -le 100; then
		echo $swappiness > /proc/sys/vm/swappiness
		sed -i '/vm.swappiness/s/^.*$/vm.swappiness = '$swappiness'/' $SYSCTL_CONF
	else
		msg "The swappiness must be a number between 0 and 100"
	fi

elif test "$action" = "usb_swap_act"; then
	if test "$usb_swap" = "Enable"; then
		sed -i '/USB_SWAP/d' $CONFT >& /dev/null
		echo USB_SWAP=yes >> $CONFT
	elif test "$usb_swap" = "Disable"; then
		sed -i '/USB_SWAP/d' $CONFT >& /dev/null
	fi

elif test "$action" = "recreate_swap_act"; then
	# FIXME: USB_SWAP is not respected
	sdevs=$(awk '/\/dev\//{print $1}' $SWAPP)
	swapoff -a >& /dev/null
	touch -r $FSTAB /tmp/fstab_date
	sed -i '/swap/d' $FSTAB
	for i in $sdevs; do
		mdadm --detail --test $i >& /dev/null
		if test $? != 4; then # RAID
			mdadm --stop $i >& /dev/null
		fi
	done

	for i in /dev/sd?; do
		p=$(sgdisk -p $i | awk '/8200/{ if ($6 == 8200) print $1}')
		if test -n "$p"; then
			mdadm --zero-superblock $i$p >& /dev/null
			mkswap  $i$p >& /dev/null
			echo "$i$p none swap pri=1 0 0" >>  $FSTAB
		fi
	done
	swapon -a -p1 >& /dev/null
	touch -r /tmp/fstab_date $FSTAB

elif test "$action" = "load_eject_act"; then
	if test -n "$Eject"; then
		bay_eject $Eject
	elif test -n "$Load"; then
		bay_eject $Load -r
	fi

elif test "$action" = "wake_standby_act"; then
	if test -n "$StandbyNow"; then
		sync
		sleep 3
		hdparm -y /dev/$StandbyNow >& /dev/null
	elif test -n "$WakeupNow"; then
		hdparm -t /dev/$WakeupNow >& /dev/null
	fi
fi

#enddebug
gotopage /cgi-bin/diskutil.cgi

