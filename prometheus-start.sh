#!/bin/sh

set -e

if [ -f "prometheus.pid" ]; then
    PREV_PID=`cat prometheus.pid`
    if kill -0 $PREV_PID 2>/dev/null; then
        echo "Prometheus is already running as $PREV_PID"
        exit 1
    fi
fi

STORAGE_DAYS=60

# Prometheus doesn't understand "days" as a unit
STORAGE_HOURS=$(( $STORAGE_DAYS * 24 ))

nohup ~prometheus/prometheus/prometheus -config.file=prometheus.yaml \
    -storage.local.path=metrics \
    -storage.local.retention=${STORAGE_HOURS}h \
    -web.external-url=/ &
PID=$!

echo $PID > prometheus.pid

