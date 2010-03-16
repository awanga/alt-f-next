#!/bin/sh

PATH=$PATH:/ffp/bin/:ffp/sbin

download() {
    wget -q http://www.inreto.de/dns323/fun-plug/0.5/packages/$1 \
        -O /tmp/$1
    if test $? = 1; then
        wget -q http://www.inreto.de/dns323/fun-plug/0.5/extra-packages/All/$1 \
        -O /tmp/$1
        return $?
    fi
    return 0
}

. common.sh
check_cookie
read_args

#debug

if test -n "$Remove"; then
#    echo "removing $Remove<br>"
    /ffp/sbin/funpkg -r $Remove >/dev/null 2>&1

elif test -n "$Install"; then
#    echo "installing $Install<br>"
    download $Install.tgz
    if test $? = 0; then
        /ffp/sbin/funpkg -i /tmp/$Install.tgz >/dev/null 2>&1
        rm /tmp/$Install.tgz
    fi

elif test -n "$Update"; then
#   echo "Updating $Update<br>"
    download $Update.tgz
    if test $? = 0; then
# FIXME -- get and use currently installed package    
#        for i in $(grep -e '/ffp/start/.*.sh' -e '/ffp/etc/.*.conf' /ffp/var/packages/$Update); do
#            cp $i $i-safe
#        done
        /ffp/sbin/funpkg -u /tmp/$Update.tgz >/dev/null 2>&1
        rm /tmp/$Update.tgz
    fi
fi

#enddebug
gotopage /cgi-bin/packages.cgi



