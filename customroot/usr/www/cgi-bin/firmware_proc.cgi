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
html_header
echo "<pre>"

tfile=/tmp/$$-$RANDOM
len=$(expr $(stat -t $file | cut -d" " -f2) - ${#delim_line} - 3 )
#head -c $len $file > $tfile
dd if=$file of=$tfile bs=$len count=1 >/dev/null 2>&1

mv $tfile $file

if ! test -s $file; then
	rm $file
	cat<<-EOF
		</pre><center><br>
		<form action="/cgi-bin/firmware.cgi" method="post">
		File is empty <input type="submit" value="Retry">
		</form></center></body></html>
	EOF
	exit 0
fi

cd /tmp
fw_version=$(dns323-fw -s $file)
st=$?

rm $file >/dev/null 2>&1

if test $st = "1"; then
	rm kernel initramfs defaults >/dev/null 2>&1
	cat<<-EOF
		</pre><center>
		<form action="/cgi-bin/firmware.cgi" method="post">
		Does not seems to be a legitime firmware file
		<input type="submit" value="Retry"></form></center></body></html>
	EOF
	exit 0
fi

echo -e "$fw_version\n\n<strong>Everything looks OK</strong>\n"

ls -l kernel initramfs defaults

ckflh="CHECKED"
if ! test -s defaults; then
	ckflh=""
fi

cat<<-EOF
	</pre>
	<form action="/cgi-bin/firmware2_proc.cgi" method="post">
	<p>Erase saved settings and flash new defaults file<br>(factory settings, the box IP might change)
	<input type="checkbox" $ckflh name=flash_defaults value=yes></p>
	<input type="submit" name=flash value="FlashIt">
	<input type="submit" name=flash value="Abort">
	</form></body></html>
EOF
exit 0
