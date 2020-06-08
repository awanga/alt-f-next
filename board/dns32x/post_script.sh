#!/bin/bash
# Wrapper to make firmware for alt-f boards

# if BR2_POST_SCRIPT is defined, pass on args
if test "$#" > 1; then
	shift
	./board/dns32x/mkfw.sh $@
else
	./board/dns32x/mkfw.sh
fi
