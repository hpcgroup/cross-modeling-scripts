#!/bin/bash

# turn on dry output
DRY=0
# DRY=1

# DATA_ROOT="/usr/WS1/dnicho/summer2022/resource-equivalences/data"
DATA_ROOT=${ROOT}/data
export JSON_OUTPUT="results.json"
JOB_NAME="data-collection-${APP_NAME}"
SUB_DIR=$(echo "${APP_NAME} ${ARGS} ${NRANKS} ${HPCRUN_EVENTS}" | md5sum | awk '{print $1}')
# QUEUE="pbatch"

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
            echo "mkdir -p ${WRK_DIR}"
        else
            mkdir -p ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ruby.sh"
    else
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ruby.sh"
        bash run-ruby.sh
        # sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ruby.sh
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
elif [[ ${HOST} == tioga* ]]; then
    SYSTEM="tioga"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir -p ${WRK_DIR}"
        else
            mkdir -p ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    # touch $output
    # touch $error
    ml flux_wrappers

    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-tioga.sh"
    else
        bash run-tioga.sh
        # flux batch -t ${TIME_LIMIT} -N 1 --output=${output} --error=${error} run-tioga.sh
        # sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-tioga.sh

    fi
elif [[ ${HOST} == *zaratan* ]]; then
    SYSTEM="zaratan"
    # QUEUE="standard"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        # exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir -p ${WRK_DIR}"
        else
            echo "mkdir -p ${WRK_DIR}"
            mkdir -p ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    echo "about to call sbatch"
    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-zaratan.sh"
    else
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-zaratan.sh"
        sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-zaratan.sh
    fi
elif [[ ${HOST} == mammoth* ]]; then
    SYSTEM="mammoth"
    # QUEUE="standard"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir -p ${WRK_DIR}"
        else
            echo "mkdir -p ${WRK_DIR}"
            mkdir -p ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    echo "about to call sbatch"
    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-mammoth.sh"
    else
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-mammoth.sh"
        # bash run-mammoth.sh
        sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-mammoth.sh
    fi
elif [[ ${HOST} == ipa* ]]; then
    SYSTEM="ipa"
    # QUEUE="standard"
    export WRK_DIR="${DATA_ROOT}/${SYSTEM}/${APP_NAME}/${SUB_DIR}"
    if [ -d ${WRK_DIR} ]; then 
        echo "Directory '${WRK_DIR}' already exists."
        # exit 1
    else
        if [ ${DRY} -ne 0 ]; then
            echo "mkdir -p ${WRK_DIR}"
        else
            echo "mkdir -p ${WRK_DIR}"
            mkdir -p ${WRK_DIR}
        fi
    fi

    output="${WRK_DIR}/std.out"
    error="${WRK_DIR}/std.err"

    echo "about to call sbatch"
    if [ ${DRY} -ne 0 ]; then
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ipa.sh"
    else
        echo "sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ipa.sh"
        sbatch -J ${JOB_NAME} -t ${TIME_LIMIT} -n ${NRANKS} --output ${output} --error ${error} -p ${QUEUE} run-ipa.sh
    fi
else
    echo "unknown host"
fi
