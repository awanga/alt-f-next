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

html_header
echo "<pre>"

echo -e "$res\n\n<strong>Everything looks OK</strong>\n"

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
