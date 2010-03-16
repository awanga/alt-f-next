#!/bin/sh

. common.sh
check_cookie

nm=$0
name=${nm%.cgi}
write_header $name
echo "<p>Write me</p>"

back=$(echo $HTTP_REFERER | sed -n 's|.*/cgi-bin/||p')

echo  "<form action=\"/cgi-bin/$back\">
        <input type=submit value=\"Back\"></form></body></html>"
