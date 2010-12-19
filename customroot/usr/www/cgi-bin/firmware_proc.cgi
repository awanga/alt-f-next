#!/bin/sh

# POST upload format:
# -----------------------------29995809218093749221856446032^M
# Content-Disposition: form-data; name="file1"; filename="..."^M
# Content-Type: application/octet-stream^M
# ^M    <--------- headers end with empty line
# file contents
# file contents
# file contents
# ^M    <--------- extra empty line
# -----------------------------29995809218093749221856446032--^M

# Beware: bashism $'\r' is used to handle ^M

#file=/tmp/down-fw
file=/tmp/$$-$RANDOM

#printf '\r\n'

IFS=$'\r'
read -r delim_line

IFS=''
delim_line="${delim_line}--"$'\r'

while read -r line; do
	test "$line" = '' && break
	test "$line" = $'\r' && break
done

cat > $file

. common.sh
check_cookie

html_header
echo "<pre>"

tfile=/tmp/$$-$RANDOM
len=$(expr $(stat -t $file | cut -d" " -f2) - ${#delim_line} - 3 )
#head -c $len $file > $tfile
dd if=$file of=$tfile bs=$len count=1 >/dev/null 2>&1

mv $tfile $file

if ! test -s $file; then
	rm $file
	msg "File is empty."
	exit 0
fi

cd /tmp
fw_version=$(dns323-fw -s $file)
st=$?

rm $file >/dev/null 2>&1

if test $st = "1"; then
	rm -f kernel initramfs defaults
	msg "Does not seems to be a legitime firmware file."
	exit 0
fi

echo -e "$fw_version\n\n<strong>Everything looks OK</strong>\n"

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
