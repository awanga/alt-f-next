#!/bin/sh

. common.sh
check_cookie
read_args

gotopage http://$(hostname -i | sed 's/ //'):631


