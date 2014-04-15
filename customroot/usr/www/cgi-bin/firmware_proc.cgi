#!/bin/sh

. common.sh
check_cookie

#debug

if ! upfile=$(upload_file); then
	msg "Uploading failed: $upfile"
	exit 0
fi

if ! test -s $upfile; then
	rm -f $upfile
	msg "The uploaded file is empty."
	exit 0
fi

cd /tmp
res=$(dns323-fw -s $upfile)
st=$?

rm -f $upfile

supported="D-Link DNS-320-A1/A2, D-Link DNS-321-A1/A2, D-Link DNS-323-A1/B1/C1, D-Link DNS-325-A1/A2, Conceptronic CH3SNAS, Fujitsu-Siemens DUO 35-LR"

if test $st != "0"; then
	rm -f kernel initramfs sqimage defaults
	msg "The uploaded file does not seems to be a legitimate firmware file. The error message was:\n\n\
$res\n\n\
Only firmware for the $supported is supported."
	exit 0
fi

# The dns323-fw program output identifies the firmware file, evaluate it
# Model	product_id	custom_id	model_id	sub_id	NewVersion type
# DNS323		7		1			1			1		4		0
# CH3SNAS		7		2			1			1		4		0
# DUO35-LR		7		3			1			1		4		0
# DNS321		a		1			1			1/2		0/1		1
# DNS343		9		1			1			1/2		1		2
# DNS325		0		8			5			1/2		0		3
# DNS320		0		8			7			1/2		0		4
# Alt-F-0.1B	1		2			3			4		5		0
# Alt-F-0.1RC	7		1			1			1		4		0

for i in $res; do
	if echo $i | grep -q ';'; then
		eval "$i" >& /dev/null
	fi
done

sig=${product_id}${custom_id}${model_id}${sub_id}
brd=$(cat /tmp/board)

case "$sig" in
	"0851"|"0852") ftype="DNS-325" ;;
	"0871"|"0872") ftype="DNS-320" ;;
	"a111"|"a112") ftype="DNS-321" ;;
	"9111"|"9112") ftype="DNS-343" ;;
	"7111") ftype="DNS-323" ;;
	"7211") ftype="CH3SNAS" ;;
	"7311") ftype="DUO35LR" ;;
	*) rm -f kernel initramfs sqimage defaults
		msg "This firmware file has signature \"$sig\" and does not seems to be compatible with supported firmware.\n\nOnly firmware for the $supported is supported."
		exit 0
		;;
esac

nomsg="Your box is a $brd and this firmware is for the $ftype"

case "$brd" in
	"DNS-325-A1") if test $ftype != "DNS-325"; then notcomp=yes; fi ;;
	"DNS-320-A1") if test $ftype != "DNS-320"; then notcomp=yes; fi ;;
	"DNS-321-A1") if test $ftype != "DNS-321"; then notcomp=yes; fi ;;
	"DNS-323-A1"|"DNS-323-B1"|"DNS-323-C1")
		if test $ftype != "DNS-323" -a $ftype != "CH3SNAS" -a $ftype != "DUO35LR"; then notcomp=yes; fi
		;;
	*)	notcomp=yes
		nomsg="Your box is a $brd and it is not supported.\n\nOnly the $supported boxes are supported."
		;;
esac

if test -n "$notcomp"; then
	rm -f kernel initramfs sqimage defaults
	msg "$nomsg"
	exit 0
fi

html_header "Firmware Update"

#echo "<pre>$res</pre>"

if ! test -s defaults; then
	flashvendor="disabled"
	flashnone="checked"
	flashfile=""
else
	flashvendor=""
	flashnone=""
	flashfile="checked"
fi

if echo $brd | grep -qE "DNS-325|DNS-320"; then
	try_dis="disabled"
	recover_dis="disabled"
fi

echo "<h4>Everything looks OK.<br>$nomsg.</h4>"

if losetup | grep -q /dev/mtdblock3; then
	runfromflash="disabled"
	flmsg='<h4 class="blue">Alt-F is running from flash memory,
you have to reboot into a special mode by hitting the "SpecialReboot" button
and after rebooting run again the "Firmware Updater" and hitting the "FlashIt" button.
<br>Some Alt-F firmware can be tried without flashing, by hitting the "TryIt" button.</h4>
<input type=submit name=flash value="SpecialReboot">'
fi

cat<<-EOF
	<form action="/cgi-bin/firmware2_proc.cgi" method="post">
	<strong>Flash settings handling:</strong>
	<p><input type="radio" $flashnone name=flash_defaults value="none">
	Don't erase flashed settings</p>

	<p><input type="radio" name=flash_defaults value="clear">
	Erase all flashed settings (the box IP might change)</p>

	<p><input type="radio" $flashfile $flashvendor name=flash_defaults value="flashfile">
	Erase all flashed settings and flash new settings from defaults file (factory settings, the box IP might change)</p>

	<p><input type="radio" $recover_dis $flashvendor name=flash_defaults value="recover">
	Erase all flashed settings and recover the last flash settings from vendors backup (the box IP might change)</p>
$flmsg
	<input type="submit" $runfromflash name=flash value="FlashIt" onclick="return confirm('\
THIS IS A NO RETURN POINT.\n\n\
If you continue, the current firmware will be erased and replaced by this new one.\n\
There exists the remote possibility that this operation fails, turning your box useless.\n\n\
YOUR HAVE BEEN WARNED.\n\n\
Continue?')">

	<input type="submit" $try_dis name=flash value="TryIt" onclick="return confirm('\
This action only executes the new firmware, it will not flash or change anything else.\n\n\
While testing the new firmware YOU SHOULD NOT SAVE ANY SETTINGS,\n\
because they might not be recognized by the current firmware when it runs again.\n\n\
Continue?')">

	<input type="submit" name=flash value="Abort">
	</form></body></html>
EOF
exit 0
