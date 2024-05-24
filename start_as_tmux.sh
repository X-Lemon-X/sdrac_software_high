#!/bin/bash

function start_tmux () {
  if ! tmux has-session -t $1 2>/dev/null; then
    echo $(date) "Started tmux session: $1"
    tmux new -d -s $1 bash $2
  else
    echo $(date) "Session already exists: $1"
  fi
}



DIR=$(cd "$( dirname "$0" )" && pwd)
cd $DIR

echo "Started tmux $(date)" >> $DIR/tmux.log



./auto-init-can.sh


start_tmux main $DIR/tmux/run_main.sh >> $DIR/tmux.log  
start_tmux rc $DIR/tmux/run_pilot.sh >> $DIR/tmux.log


