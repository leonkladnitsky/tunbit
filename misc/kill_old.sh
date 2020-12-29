#!/usr/bin/env bash

function join_by {
  local IFS="$1"
  shift
  echo "$*"
}

mapfile -t suspects < <(ps -ax | grep '/usr/bin/google-chrome\|/opt/google/chrome/chrome' | awk '{print $1}' | sed 's/:.*//')
#echo "Suspects:"
#echo "========="
#printf "%s," ${suspects[@]}
#printf "%s\n"

oldfags=()
for pid in ${suspects[@]}; do
#  echo "pid: $pid"
#    ps -o etimes= -p "$i" | awk '{$1=$1};1'

  lifespan_sec=$(( $(ps -o etimes= -p "$pid" | awk '{$1=$1};1') ))

  ### for lifespan more than 10 minutes ...
  if [[ ${lifespan_sec}  -gt  600 ]]
  then
    oldfags+=(${pid})
#  else
#    echo "$pid is too young to die"
  fi
done

if [[ ${#oldfags[@]} -eq 0 ]]
then
  exit
fi

ps -p $(join_by , "${oldfags[@]}") -o pid,vsz=MEMORY -o user,group=GROUP -o comm,args=ARGS, -o etimes=UPTIME >> ~/dev/tunbit/logs/kill_old.log

echo "Chromebie killer" >> ~/dev/tunbit/logs/kill_old.log
echo "[$(date)]" >> ~/dev/tunbit/logs/kill_old.log
echo "================" >> ~/dev/tunbit/logs/kill_old.log
echo "Oldfags:  ${#oldfags[@]}"
echo "========"
printf "%s\n" ${oldfags[@]}

for pid in ${oldfags[@]};
do
  sudo kill -9 ${pid}
done
