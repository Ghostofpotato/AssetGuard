#!/bin/bash

# ------------------------ Tests configuration section ------------------------

# Useful variables
STATS_MONITOR_POLL_TIME_SECS=0.1

# Benchmark configuration
: "${BT_TIME:=10}"
BT_RATE=0
BT_INPUT=./utils/test_logs.txt
BT_OUTPUT=${ASSETGUARD_HOME}/logs/alerts/alerts-ECS.json

# Engine Configurations
: "${ORCHESTRATOR_THREADS:=1}"

# ---------------------------- Engine test section ----------------------------

TEST_NAME="engine-bench-${ORCHESTRATOR_THREADS}-threads-${RANDOM}"

# check engine is running
if pgrep -x "assetguard-manager-analysisd" > /dev/null; then
    echo "assetguard-manager-analysisd will be restarted."
    pkill -f ${ASSETGUARD_HOME}/bin/assetguard-manager-analysisd
    sleep 1
fi

ASSETGUARD_ORCHESTRATOR_THREADS="${ORCHESTRATOR_THREADS}" ${ASSETGUARD_HOME}/bin/assetguard-manager-analysisd &

sleep 5

python3 ./utils/monitor.py -s $STATS_MONITOR_POLL_TIME_SECS -b assetguard-manager-analysisd -n $TEST_NAME &

MONITOR_PID=$!

go run ./utils/benchmark_tool.go -o $BT_OUTPUT -t $BT_TIME  -r $BT_RATE -i $BT_INPUT -T  | tee "engine-bench-${ASSETGUARD_ORCHESTRATOR_THREADS}-threads-${RANDOM}.log"

kill -INT $MONITOR_PID

ENGINE_FILE="monitor-${TEST_NAME}.csv"
echo "Output file: ${ENGINE_FILE}"

# ---------------------------- Test output section ----------------------------

sleep 1

python3 ./utils/process_stats.py -e "${ENGINE_FILE}"
