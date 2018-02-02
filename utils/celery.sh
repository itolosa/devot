#!/bin/bash
celery multi start worker1 -A mailer --pidfile="$HOME/devot/devot/%n.pid" --logfile="$HOME/devot/devot/%n.log"