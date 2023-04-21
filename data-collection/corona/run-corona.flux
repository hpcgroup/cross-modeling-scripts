#!/bin/bash

# input params
EXEC="${APP_NAME}"

# move into working directory
echo "Stepping into '${WRK_DIR}'..."
cd ${WRK_DIR}
printf "{\n" > ${JSON_OUTPUT}
printf "\t\"machine\": \"%s\",\n" "corona" >> ${JSON_OUTPUT}
printf "\t\"app\": \"%s\",\n" "${APP_NAME}" >> ${JSON_OUTPUT}
printf "\t\"exec\": \"%s\",\n" "${EXEC}" >> ${JSON_OUTPUT}
printf "\t\"args\": \"%s\",\n" "${ARGS}" >> ${JSON_OUTPUT}
printf "\t\"ranks\": \"%s\",\n" "${NRANKS}" >> ${JSON_OUTPUT}
printf "\t\"events\": \"%s\",\n" "${HPCRUN_EVENTS}" >> ${JSON_OUTPUT}
printf "\t\"path\": \"%s\",\n" "${WRK_DIR}" >> ${JSON_OUTPUT}


# load needed modules
module load ${MODULES}
#if [ -n ${ENV_NAME} ]; then
spack env list
spack env activate ${ENV_NAME}
#fi
spack load hpctoolkit
if [ $? -ne 0 ]; then exit 1; fi
printf "\t\"modules\": \"%s\",\n" "${MODULES}" >> ${JSON_OUTPUT}
printf "\t\"spack_env\": \"%s\",\n" "${ENV_NAME}" >> ${JSON_OUTPUT}
source /usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/utilities.bash


EXEC_PATH=`which ${EXEC}`
if [ $? -ne 0 ]; then exit 1; fi
printf "\t\"exec_path\": \"%s\",\n" "${EXEC_PATH}" >> ${JSON_OUTPUT}


# run app with default timing
echo "Running on on ${NRANKS} ranks..."
START=$(timestamp)
flux run -n ${NRANKS} -c 1 -g 1 \
    hpcrun -o hpctoolkit-measurements ${HPCRUN_EVENTS} \
    ${EXEC} ${ARGS} 2> ${WRK_DIR}/std.err 1> ${WRK_DIR}/std.out
END=$(timestamp)
DURATION=$(diff_minutes $START $END)
echo "Took ${DURATION} minutes."
printf "\t\"duration\": \"%s\"\n" "${DURATION}" >> ${JSON_OUTPUT}
printf "}\n" >> ${JSON_OUTPUT}


# re-process measurements dir with hpcstruct
echo "Parsing measurements with hpcstruct..."
START=$(timestamp)
hpcstruct hpctoolkit-measurements
END=$(timestamp)
DURATION=$(diff_minutes $START $END)
echo "Took ${DURATION} minutes."

# build profile database
echo "Creating database..."
START=$(timestamp)
hpcprof --metric-db yes -o hpctoolkit-database \
    hpctoolkit-measurements
END=$(timestamp)
DURATION=$(diff_minutes $START $END)
echo "Took ${DURATION} minutes."

# collect counters
echo "Parsing counters..."
START=$(timestamp)
ml python/3.10.8
export PYTHONPATH="${PYTHONPATH}:/usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/corona/hpctoolkit/tests2/lib/python"
python3 /usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/corona/read_v4_counters.py \
    --input hpctoolkit-database --append ${JSON_OUTPUT}
END=$(timestamp)
DURATION=$(diff_minutes $START $END)
echo "Took ${DURATION} minutes."

# cleanup
echo "Cleaning up..."
START=$(timestamp)
#rm "${EXEC}.hpcstruct"
rm -r "hpctoolkit-measurements"
rm -r "hpctoolkit-database"
END=$(timestamp)
DURATION=$(diff_minutes $START $END)
echo "Took ${DURATION} minutes."