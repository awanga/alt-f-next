
opts="-i"

sshd_inetd="\tstream\ttcp\tnowait\troot\t/usr/sbin/sshd\tsshd "

cmt=""
if grep -q '^#.*\/usr\/sbin\/sshd' $CONF_INETD; then
	cmt="#"
fi
 
if test "$sshd_port" = 22; then
	sed -i "/\/usr\/sbin\/sshd/s|^.*$|${cmt}ssh${sshd_inetd}${opts}|" $CONF_INETD
elif test "$sshd_port" = 2222; then
	sed -i "/\/usr\/sbin\/sshd/s|^.*$|${cmt}ssh_alt${sshd_inetd}${opts}|" $CONF_INETD
fi
