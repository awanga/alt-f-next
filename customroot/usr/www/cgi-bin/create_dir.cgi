#!/bin/sh

. common.sh
check_cookie
read_args

#echo "<pre>$(set)</pre>"

newdir="$(httpd -d $newdir)"
if test -d "$(dirname "$newdir")"; then
	mkdir -p "$newdir"
fi

gotopage $HTTP_REFERER

#echo "</body></html>"
exit 0
