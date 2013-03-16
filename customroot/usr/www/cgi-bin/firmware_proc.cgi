#!/bin/sh

. common.sh
check_cookie

upfile=$(upload_file)

if ! test -s $upfile; then
	rm -f $upfile
	msg "File is empty."
	exit 0
fi

cd /tmp
res=$(dns323-fw -s $upfile)
st=$?

rm -f $upfile

if test $st != "0"; then
	rm -f kernel initramfs defaults
	msg "Does not seems to be a legitime firmware file."
	exit 0
fi

# The dns323-fw program output identifies the firmware file, evaluate it
# Model	product_id	custom_id	model_id	sub_id	NewVersion type
# DNS321		a		1			1			2		1		1
# DNS323		7		1			1			1		4		0
# CH3SNAS		7		2			1			1		4		0
# DUO 35-LR		7		3			1			1		4		0
# Alt-F-0.1B	1		2			3			4		5		0
# Alt-F-0.1RC	7		1			1			1		4		0

# Board/Firmware known compatibility.
# It is not clear cut, as the Alt-F firmware has a DNS323 signature
#
#    DNS321 DNS323 CH3SNAS DUO35LR
# A1  X       V      ?      ?
# B1  X       V      V      V
# C1  X       V      ?      ?
# D1  V       V      X      X

for i in $res; do
	if echo $i | grep -q ';'; then
		eval "$i" >& /dev/null
	fi
done

sig=${product_id}${custom_id}${model_id}${sub_id}
brd=$(cat /tmp/board)

case $sig in
	"a112") ftype="DNS-321" ;;
	"7111") ftype="DNS-323" ;;
	"7211") ftype="CH3SNAS" ;;
	"7311") ftype="DUO35LR" ;;
	"1234") ftype="Alt-F-0.1Bx" ;;
	*) 
		rm -f kernel initramfs defaults
		msg "This firmware file has signature $sig and does not seems to be compatible with the\nD-Link DNS-321, D-Link DNS-323, Conceptronic CH3SNAS or Fujitsu-Siemens DUO 35-LR."
		exit 0
		;;
esac

if test "$brd" = "D1" -a "$ftype" != "DNS-321" -a "$ftype" != "DNS-323"; then
	rm -f kernel initramfs defaults
	msg "Your box is a DNS-321 and this firmware file was not designed for it".
elif test "$ftype" = "DNS-321" -a $brd != "D1"; then
	rm -f kernel initramfs defaults
	msg "This firmware file was designed for a DNS-321 and your box is not a DNS-321.".
fi

html_header
echo "<h2><center>Firmware Updater</center></h2><pre>"

echo "$res</pre>"

if ! test -s defaults; then
	flashvendor="disabled"
	flashnone="checked"
	flashfile=""
else
	flashvendor=""
	flashnone=""
	flashfile="checked"
fi

echo "<h4>Everything looks OK. The firmware file is for a $ftype and you have a rev-$brd board.</h4>"

if losetup  | grep -q /dev/mtdblock3; then
	runfromflash="disabled"
	flmsg="<h4><font color=blue>Alt-F is running from flash memory,
you have to reboot into a special mode before being able to flash.<br>You can however TryIt first.</font></h4>
<input type=submit name=flash value=\"SpecialReboot\">"
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

	<p><input type="radio" $flashvendor name=flash_defaults value="recover">
	Erase all flashed settings and recover the last flash settings from vendors backup (the box IP might change)</p>
$flmsg
	<input type="submit" $runfromflash name=flash value="FlashIt" onclick="return confirm('\
THIS IS A NO RETURN POINT.\n\n\
If you continue, the current firmware will be erased and replaced by this new one.\n\
There exists the remote possibility that this operation fails, turning your box useless.\n\n\
YOUR HAVE BEEN WARNED.\n\n\
Continue?')">

	<input type="submit" name=flash value="TryIt" onclick="return confirm('\
This action only executes the new firmware, it will not flash or change anything else.\n\n\
While testing the new firmware YOU SHOULD NOT SAVE ANY SETTINGS,\n\
because they might not be recognized by the current firmware when it runs again.\n\n\
Continue?')">

	<input type="submit" name=flash value="Abort">
	</form></body></html>
EOF
exit 0
