#!/bin/bash
DIR=$(cd "$( dirname "$0" )" && pwd)
cd $DIR
cd ..

source /opt/ros/humble/setup.bash
source .venv/bin/activate
python3 lib/main.py 