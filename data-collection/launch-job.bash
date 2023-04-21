#!/bin/bash

# turn on dry output
DRY=0

DATA_ROOT="/usr/WS1/dnicho/summer2022/resource-equivalences/data"
export JSON_OUTPUT="results.json"
JOB_NAME="data-collection-${APP_NAME}"
SUB_DIR=$(echo "${APP_NAME} ${ARGS} ${NRANKS} ${HPCRUN_EVENTS}" | md5sum | awk '{print $1}')
QUEUE="pbatch"

HOST=$(hostname)

if [[ ${HOST} == quartz* ]]; then
    SYSTEM="quartz"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir ${WRK_DIR}"
        else
            mkdir ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-quartz.sbatch"
    else
        sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-quartz.sbatch
    fi
elif [[ ${HOST} == ruby* ]]; then
    SYSTEM="ruby"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir ${WRK_DIR}"
        else
            mkdir ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ruby.sbatch"
    else
        sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ruby.sbatch
    fi

elif [[ ${HOST} == lassen* ]]; then
    SYSTEM="lassen"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir ${WRK_DIR}"
        else
            mkdir ${WRK_DIR}
        fi
    fi

    if [ ${RUN_AS_JOB} -ne 0 ]; then
        output="${WRK_DIR}/std.out"
        error="${WRK_DIR}/std.err"

        if [ ${DRY} -ne 0 ]; then
            echo "bsub -J ${JOB_NAME} -W ${TIME_LIMIT} -nnodes 1 -o ${output} -e ${error} -q ${QUEUE} run-lassen.bsub"
        else
            bsub -J ${JOB_NAME} -W ${TIME_LIMIT} -nnodes 1 -o ${output} -e ${error} -q ${QUEUE} run-lassen.bsub
        fi
    else
        if [ ${DRY} -ne 0 ]; then
            echo "bash run-lassen.bsub"
        else
            bash run-lassen.bsub
        fi
    fi

elif [[ ${HOST} == corona* ]]; then
    SYSTEM="corona"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir ${WRK_DIR}"
        else
            mkdir ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"
    ml flux_wrappers

    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-corona.flux"
    else
        flux batch -t ${TIME_LIMIT} -N 1 --output=${output} --error=${error} run-corona.flux
    fi
else
    echo "unknown host"
fi
