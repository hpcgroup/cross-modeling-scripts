#!/bin/bash

# constants
export MODULES="intel mvapich2 hpctoolkit/2021.10 papi"
export ENV_NAME="resource-equivalence-quartz"
export TIME_LIMIT="00:15:00"

# ROOT="/scratch/zt1/project/bhatele-lab/user/amovsesy/cross-modeling-scripts/data-collection"
ROOT="/Users/movsesyanae/Programming/Research/LLNL/cross-modeling-scripts/data-collection"
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
    "-e PAPI_BR_INS -e PAPI_LD_INS -e PAPI_SR_INS -e PAPI_TOT_INS"
    "-e PAPI_L1_LDM -e PAPI_L1_STM -e PAPI_L2_LDM -e PAPI_L2_STM -e EPT"
    "-e bdw_ep::FP_ARITH:SCALAR_SINGLE -e bdw_ep::FP_ARITH:SCALAR_DOUBLE -e bdw_ep::ARITH" 
    "-e IO -e PAPI_MEM_WCY -e REALTIME"
)

for FILE in $CONFIG_DIR/*; do 
    schedule_config $FILE
done
# export APP_NAME="laghos"

