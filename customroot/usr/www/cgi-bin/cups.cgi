#!/bin/sh

. common.sh
check_cookie
read_args

rccups status >& /dev/null
if test $? != 0; then
	msg "cups must be running in order to configure it."
fi

gotopage http://$(hostname -i | sed 's/ //'):631


