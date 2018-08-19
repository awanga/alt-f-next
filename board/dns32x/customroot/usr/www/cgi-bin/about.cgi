#!/bin/sh

. common.sh
write_header "About Alt-F"

cat<<-EOF

<p>Alt-F is a <a href="http://en.wikipedia.org/wiki/Free_software">free</a>
alternative firmware for the D-Link DNS-320/320L/321/323/325/327L and compatible NAS.
<p>
<a href="http://sourceforge.net/projects/alt-f" target=_blank>Main site</a><br>
<a href="http://groups.google.com/group/alt-f" target=_blank>Support Forum</a><br>
<a href="http://sourceforge.net/p/alt-f/wiki/Home" target=_blank>Wiki</a><br> 

<h3>Copyright</h3>	
<pre>$(cat /LICENSE)</pre>

<h3>License</h3>
<pre>$(cat /COPYING)</pre>

</body></html>
EOF

