#!/bin/bash

# input params
EXEC="${APP_NAME}"

# move into working directory
echo "Stepping into '${WRK_DIR}'..."
cd ${WRK_DIR}
printf "{\n" > ${JSON_OUTPUT}
printf "\t\"machine\": \"%s\",\n" "zaratan" >> ${JSON_OUTPUT}
printf "\t\"app\": \"%s\",\n" "${APP_NAME}" >> ${JSON_OUTPUT}
printf "\t\"exec\": \"%s\",\n" "${EXEC}" >> ${JSON_OUTPUT}
printf "\t\"args\": \"%s\",\n" "${ARGS}" >> ${JSON_OUTPUT}
printf "\t\"ranks\": \"%s\",\n" "${NRANKS}" >> ${JSON_OUTPUT}
printf "\t\"events\": \"%s\",\n" "${HPCRUN_EVENTS}" >> ${JSON_OUTPUT}
printf "\t\"path\": \"%s\",\n" "${WRK_DIR}" >> ${JSON_OUTPUT}

# load needed modules
module load ${MODULES}
spack env activate ${ENV_NAME}
if [ $? -ne 0 ]; then exit 1; fi
printf "\t\"modules\": \"%s\",\n" "${MODULES}" >> ${JSON_OUTPUT}
printf "\t\"spack_env\": \"%s\",\n" "${ENV_NAME}" >> ${JSON_OUTPUT}
source /usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/utilities.bash

# hpctoolkit -- static analysis
EXEC_PATH=`which ${EXEC}`
if [ $? -ne 0 ]; then exit 1; fi
printf "\t\"exec_path\": \"%s\",\n" "${EXEC_PATH}" >> ${JSON_OUTPUT}
hpcstruct ${EXEC_PATH} -o "${EXEC}.hpcstruct"

# run app with default timing
echo "Running on on ${NRANKS} ranks..."
START=$(timestamp)
srun -n ${NRANKS} \
    hpcrun -o "hpctoolkit-measurements" ${HPCRUN_EVENTS} \
    ${EXEC} ${ARGS}
END=$(timestamp)
DURATION=$(diff_minutes $START $END)
echo "Took ${DURATION} minutes."
printf "\t\"duration\": \"%s\"\n" "${DURATION}" >> ${JSON_OUTPUT}
printf "}\n" >> ${JSON_OUTPUT}

# build profile database
#export HPCRUN_IGNORE_THREAD=1
srun -n ${NRANKS} \
    hpcprof-mpi --metric-db yes -S "${EXEC}.hpcstruct" -o "hpctoolkit-database" \
    "hpctoolkit-measurements" 

# collect counters
python3 /usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/read-counters.py \
    --input hpctoolkit-database --append ${JSON_OUTPUT}

# cleanup
rm "${EXEC}.hpcstruct"
rm -r "hpctoolkit-measurements"
rm -r "hpctoolkit-database"