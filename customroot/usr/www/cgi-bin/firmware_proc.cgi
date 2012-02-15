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

# Model			product_id	custom_id	model_id	sub_id	NewVersion
# DNS323		7			1			1			1		4
# CH3SNAS		7			2			1			1		4
# Alt-F-0.1B	1			2			3			4		5
# Alt-F-0.1RC	7			1			1			1		4

for i in $res; do
	if echo $i | grep -q ';'; then
		eval "$i" >& /dev/null
	fi
done

sig=${product_id}${custom_id}${model_id}${sub_id}

case $sig in
	"7111") ftype="DNS-323" ;;
	"7211") ftype="CH3SNAS" ;;
	"1234") ftype="Alt-F-0.1Bx" ;;
	*) 
		rm -f kernel initramfs defaults
		msg "$sig Does not seems to be a firmware file for the DNS323 nor the CH3SNAS."
		exit 0
		;;
esac

html_header
echo "<h2><center>Firmware Updater</center></h2><pre>"

echo -e "$res\n\n<strong>Everything looks OK, it is a $ftype compatible firmware file</strong>\n"

ls -l kernel initramfs defaults

if ! test -s defaults; then
	flashvendor="disabled"
	flashnone="checked"
	flashfile=""
else
	flashvendor=""
	flashnone=""
	flashfile="checked"
fi

cat<<-EOF
	</pre>
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

	<input type="submit" name=flash value="FlashIt" onclick="return confirm('\
THIS IS A NO RETURN POINT.\n\n\
If you continue, the current firmware will be erased and replaced by this new one.\n\
There exists the remote possibility that this operation fails, turning your box useless.\n\n\
YOUR HAVE BEEN WARNED.\n\n\
Continue?')">

	<input type="submit" name=flash value="TryIt" onclick="return confirm('\
This action only executes the new firmware, it will not flash or change anything else.\n\n\
While testing the new firmware YOU SHOULD NOT SAVE ANY SETTINGS,\n\
because they might not be recognized by the current firmwarem when it runs again.\n\n\
Continue?')">

	<input type="submit" name=flash value="Abort">
	</form></body></html>
EOF
exit 0
