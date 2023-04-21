#!/bin/bash
# Temporary script for reading HPCToolkit profiles, calculating relevant counter values,
# and storing them in a json. This is to help clear up space and inodes. The
# data collection scripts now do this automatically. This is for older data.

ROOT="/usr/WS1/dnicho/summer2022/resource-equivalences/data/quartz/laghos"

cd ${ROOT}
dirs=$(ls)

for dir in ${dirs}; do

    if [ -d "${dir}/hpctoolkit-database" ]; then

        python3 /usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/read-counters.py --input ${dir}/hpctoolkit-database --append ${dir}/results.json
        if [ $? -eq 0 ]; then
            rm -r ${dir}/hpctoolkit-database
        fi

    fi

done