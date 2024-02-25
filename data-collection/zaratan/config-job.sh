#!/bin/bash

# constants
# export MODULES="intel mvapich2 hpctoolkit/2021.10 papi"
export ENV_NAME="cpu-apps"
export TIME_LIMIT="00:15:00"
export HOST="zaratan"
export QUEUE="standard"
echo $HOST

export ROOT="/scratch/zt1/project/bhatele-lab/user/amovsesy/performance-modeling/cross-modeling-scripts/data-collection"
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
    "-e REALTIME"
)

for FILE in $CONFIG_DIR/*; do 
    schedule_config $FILE
done
# export APP_NAME="laghos"

