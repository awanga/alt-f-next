export TERM=linux
export HOME=/root
export PS1="[\u@\h]\# "

alias his="cat ~/.ash_history | grep "
alias l="ls -la"
alias mt='top -bn1 | grep -v "\[.*\]$"'

stty stop ^Q
resize
