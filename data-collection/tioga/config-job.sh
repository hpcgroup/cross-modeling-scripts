#!/bin/bash

# constants
export ROOT="/p/lustre1/amovses/cross-modeling-scripts/data-collection"
export MODULES=""
export ENV_NAME="cpu-apps-generic"
export TIME_LIMIT="=15m"
export QUEUE="pci"

# export ROOT="/Users/movsesyanae/Programming/Research/LLNL/cross-modeling-scripts/data-collection"
CONFIG_DIR="${ROOT}/app-arg-configuration/configs"

# enumerate (args, nranks, hpcrun_events) paired with wall time
function run_job {
    export APP_NAME="$1"
    export ARGS="$2"
    export NRANKS="$3"
    export HPCRUN_EVENTS="$4"
    bash ${ROOT}/launch-job.bash
}

function schedule_config {
    # set filename
    FILE="$1"

    # read file into array
    mapfile -t arr < $FILE
    # read app name and number of ranks
    APP_NAME="${arr[0]}"
    nranks="${arr[1]}"
    args=("${arr[@]:2}")

    # iterate over args
    for arg in "${args[@]}"; do
        for evt in "${hpcrun_events[@]}"; do
            run_job "$APP_NAME" "$arg" "$nranks" "$evt"
            if [ $? -eq 0 ]; then
                sleep 0.5
            fi
        done
    done
}

declare -a hpcrun_events=(
    "-e perf::cpu-cycles"
    "-e perf::branch-load-misses"
    "-e perf::branch-misses"
    "-e perf::context-switches"
    "-e perf::iTLB-load-misses"
    "-e perf::instructions"
    "-e perf::cache-misses"
    "-e perf::branch-instructions"
    "-e perf::major-faults"
    "-e perf::L1-dcache-load-misses"
    "-e perf::branch-loads"
    "-e perf::minor-faults"
    "-e perf::cache-references"
    "-e perf::task-clock"
    "-e perf::page-faults"
    "-e perf::cpu-migrations"
    "-e perf::L1-icache-load-misses"
    "-e perf::cpu-clock"
    "-e perf::L1-dcache-loads"
    "-e perf::dTLB-load-misses"
    "-e perf::dTLB-loads"
)

for FILE in $CONFIG_DIR/*; do 
    schedule_config $FILE
done
# export APP_NAME="laghos"

