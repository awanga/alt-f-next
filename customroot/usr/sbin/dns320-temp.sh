#!/bin/sh
#
# Get temperature from a Dlink DNS-320's microcontroller
#
# Copyright (C) 2012 Jamie Lentin <jm@lentin.co.uk>
#
# This file is licensed under the terms of the GNU General Public
# License version 2. This program is licensed "as is" without any
# warranty of any kind, whether express or implied.
#
# Adapted to Alt-F by: Joao Cardoso

# Protocol:
# == Request ==
#  0xf0 0xf0 0x10 0x04
#  0x02 0x00 0x00 0x00
#  0x00 0x00 0x00 0x00
#  0x00 0xf6 0xf6 0xf6
# == Response ===
# General return format:-
#  0xf0 0xf0 0xd0 (x)
#  0x02 (t)  0x00 0x00
#  0x00 0x00 0x00 0x00
#  0x00 (cs) (cs) (cs)
#   (x) = 0x00 or 0x04
#   (t) = Temperature in degC
#  (cs) = 0xb6 + (t)
#
# Malformed:-
# 28degC: 0 0 0 0 0 0 0 d2 d2 d2

# serial device
sdev=/dev/ttyS1

# output file
outf=/tmp/sys/temp1_input

# sysctrl is asynchronously reading the out file, set a lock
lockdir="/var/lock/temp-lock"

write_temp() {
	i=100
	while ! mkdir $lockdir >& /dev/null; do
		if test $((i--)) -eq 0; then
			if ! test -f $lockdir/pid; then # assume OK, continue
				logger -st dns320-temp "no lock owner pid"
			else
				lpid=$(cat $lockdir/pid)
				if test "$$" = "$lpid"; then # assume OK, continue
					logger -st dns320-temp "that's me!"
				elif ! kill -0 $(cat $lockdir/pid) >& /dev/null; then # stale lock, continue
					logger -st dns320-temp "stale $lockdir"
				else
					imsg="Can't get lock, \"$lockdir\" exists, exiting."
					echo "<li><pre>dns320-temp: $imsg</pre>" >> /var/log/systemerror.log
					logger -st dns320-temp "$imsg"
					exit 1
				fi
			fi
			break
		fi
		usleep 100000
	done
	echo $$ > $lockdir/pid
	echo $1 > $outf # all the above just because of this line
	rm -rf $lockdir
}

unset LANG	# A UTF-8 LANG will cause bashes read to read multibyte characters
IFS=''	# Stop read treating " " as a field separator

[ "$1" = "-v" ] && verbose=1

# Set up serial port
stty -F $sdev cs8 -cstopb -crtscts -ixon -ixoff -ignpar cread 19200

while true; do
	(
		# Wait for main thread to be ready before issuing command
		usleep 100000
		# D-link did "sleep 0.2s" between each of these, doesn't seem to help
		echo -ne "\xf0\xf0\x10\x04\x02"
		echo -ne "\x00\x00\x00\x00"
		echo -ne "\x00\x00\x00\x00"
		echo -ne "\xf6\xf6\xf6"
	) > $sdev &

	# don't like this, but seems to be working
	# -is the sub-shell necessary?
	# -wouldn't be better to always try to sync with a pattern, limited to 16 bytes, instead?
	(
		debug=""
		pos=0
		temp=0
		ch=0 ; p1=0 ; p2=0
		# busybox read doesn't has -d option, fix 10 degrees issue for packet=std bellow
		while read  -r -n 1 -t 2 -s raw; do
			ch=$(printf "%d" "'$raw")
			debug="`printf "$debug %x" $ch`"

			# If have initial 0xf0 0xf0 0xd0, then know where temperature is
			[ "$pos" = "2" -a "$p2" -eq "240" \
							-a "$p1" -eq "240" \
							-a "$ch" -eq "208" ] && packet="std"
			[ "$pos" = "5" -a "$packet" = "std" ] && { [ -z "$raw" ] && temp=10 || temp="$ch"; }

			# Three equal non-null bytes is the checksum at the end
			[ "$ch" -gt "0" -a "$p2" -eq "$ch" \
							-a "$p1" -eq "$ch" ] && { checksum="$ch"; break; }
			pos=$(($pos+1))
			p2=$p1
			p1=$ch
		done

		[ -n "$verbose" ] && logger -st dns320-temp "debug: $debug"
		if [ "$temp" -gt "0" ]; then
			# Got a temperature
			write_temp $(($temp*1000))
		elif [ -n "$checksum" ]; then
			# Found a checksum that tells us the temperaturae
			write_temp $((($checksum-182)*1000))
		else
			logger -st dns320-tmp "Unknown response: $debug"
		fi
	) < $sdev || exit 1

	sleep 15
done

# generate a test file with both std and chk packets
#
#for f in `seq 0 50`; do
#	echo -ne "\xf0\xf0\xd0\x04\x02\x$(printf "%x" $f)\x00\x00\x00\x00\x00\x00\x00\xb6\xb6\xb6"
#	t=$(printf "%x" $((f+182)))
#	echo -ne "\xf0\x00\xd0\x04\x02\x04\x00\x00\x00\x00\x00\x00\x00\x$t\x$t\x$t"
#done > testfile
