#!/usr/bin/env bash

python ~/dev/tunbit/manage.py clean_pyc

find ~/dev/tunbit/ -name "*.pyc" -type f -delete
~/dev/tunbit/misc/kill_old.sh
~/dev/tunbit/misc/clear_logs.sh
sudo apache2ctl restart
