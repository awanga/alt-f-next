#!/bin/sh

. common.sh
check_cookie

nm=$0
name=${nm%.cgi}
write_header $name
echo "<p>Write me</p>"
back_button
echo "</body></html>"
