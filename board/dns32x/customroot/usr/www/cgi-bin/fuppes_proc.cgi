#!/bin/sh

. common.sh
check_cookie
read_args

#debug

CONFF=/etc/fuppes/fuppes.cfg

if test -n "$webPage"; then
	FUPPES_PORT=$(sed -n 's/.*<http_port>\(.*\)<\/http_port>/\1/p' $CONFF)
	embed_page "http://${HTTP_HOST%%:*}:$FUPPES_PORT/presentation/config.html" "Fuppes Page"
fi

# mark lines, to undo changes on error
sed -i '/<shared_objects>/,/<\/shared_objects>/ {
/<dir>/s/^.*$/##!##&/
}' $CONFF

subd="<shared_objects>"
for i in $(seq 1 $cnt); do
	d="$(eval echo \$sdir_$i)"
	if test -z "$d"; then continue; fi
	s=$(httpd -d $d)
	if ! test -d "$s"; then
		sed -i -e 's/^##!##//' -e '/<!!#!!dir/d' $CONFF # undo changes
		msg "At least one directory does not exist."
	fi
	sed -i '/<shared_objects>/a \
    <!!#!!dir>'"$s"'</dir>' $CONFF # mark additions, to undo on error
done

# delete initial entries, update additions
sed -i -e '/^##!##.*<dir>/d' -e 's/<!!#!!dir/<dir/' $CONFF

if test -z "$ENABLE_WEB"; then
	subs="<ip>0.0.0.0</ip>"
fi

sed -i '/<allowed_ips>/,/<\/allowed_ips>/c \
    <allowed_ips> \
      '$subs' \
    </allowed_ips> ' $CONFF

rcfuppes status >& /dev/null
if test $? = 0; then
	rcfuppes force-reload >& /dev/null
fi

#enddebug
gotopage /cgi-bin/user_services.cgi

