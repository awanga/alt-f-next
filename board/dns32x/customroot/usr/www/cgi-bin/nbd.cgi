#!/bin/sh

# cnt, share, host, opts
spit_exports() {
	cnt=$1
	share=$2
	host=$3
	opts=$4
	cat<<-EOF
		<tr><td align=center><input type=checkbox $sel name=xcmtd_$cnt value="#"></td>
		<td><input type=text size=10 id=expo_$cnt name=expo_$cnt value="$expo"></td>
		<td><input type=text size=10 id=dev_$cnt name=dev_$cnt value="$dev" ></td>
		<td><input type=text size=10 id=mode_$cnt name=mode_$cnt value="$mode" ></td>
		</tr>
	EOF
}

source ./common.sh
check_cookie
read_args
write_header "NBD exports Setup"

#debug

CONFX=/etc/nbd-server/config
CONFM=/etc/misc.conf

if test -f $CONFM; then
	. $CONFM
fi


cat<<-EOF
       <form name=expdir action=nbd_proc.cgi method="post" >
		<fieldset>
		<legend>Folders to export to other hosts</legend>
		<table>
		<tr align=center>
		<th>Disable</th>
		<th>Export</th>
		<th>Device</th>
		<th>Readonly</th>
		</tr>
EOF

# -- hostip=$(hostname -i)
# -- netmask=$(ifconfig eth0 | awk '/inet addr/ { print substr($4, 6) }')
# -- eval $(ipcalc -n $hostip $netmask) # evaluate NETWORK
# -- def_ip="$NETWORK/$netmask"

cnt=0
if test -e $CONFX; then

  while IFS= read -r var; do

        if [ ! -z $expo ] && [ ! -z $dev ] && [ ! -z $mode ]; then
    	    spit_exports "$cnt" "$expo" "$dev" "$mode"
            unset expo dev mode
	    cnt=$((cnt+1))
        fi 

        echo "$var" | grep -q "^#" 2> /dev/null && continue
        echo "$var" | grep -q "^\[generic]" 2> /dev/null && continue
        echo "$var" | grep -q "\[.*\]" 2> /dev/null && expo=`echo $var |sed -e 's/\[\(.*\)\]/\1/'`
        echo "$var" | grep -q "exportname"2> /dev/null  && dev=`echo $var |sed -e 's/exportname = \(.*\)/\1/'`
        echo "$var" | grep -q "readonly" 2>/dev/null && mode=`echo $var |sed -e 's/readonly = \(.*\)/\1/'`

  done < $CONFX
fi

for i in $(seq $((cnt+1)) $((cnt+3))); do
	spit_exports $i
done

cat<<-EOF
 	</table><input type=hidden name="n_exports" value="$cnt">
 	</fieldset>
EOF

# --- if ! aufs.sh -s >& /dev/null; then
# --- 	dnfs_dis="disabled"	
# --- fi
# --- 
# --- if test -n "$DELAY_NFS"; then
# --- 	dnfs_chk="checked"
# --- fi
# --- 
# --- 
# --- mktt dnfs_tt "Delay NFS start on boot until the Alt-F packages folder becomes available"
# --- mktt rmtab_tt "Remove remote mount entries at service start."
# --- 
# --- 	<table>
# --- 	<tr><td>Delay NFS start on boot</td><td><input $dnfs_dis $dnfs_chk type=checkbox name=delay_nfs value=yes $(ttip dnfs_tt)></td></tr>
# --- 	</table>
cat<<-EOF
	<p><input type="submit" name="submit" value="Submit">$(back_button)
	</form></body></html>
EOF
