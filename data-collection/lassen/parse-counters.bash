#!/bin/bash


cd /usr/WS1/dnicho/summer2022/resource-equivalences/data/lassen/laghos
subdirs=$(ls)

for subdir in $subdirs; do
    if [ -d $subdir/hpctoolkit-database ]; then
        echo $subdir
        cd $subdir
        python3 /usr/WS1/dnicho/summer2022/resource-equivalences/data-collection/read-counters.py \
            --input hpctoolkit-database --append results.json
        if [ $? -ne 0 ]; then
            echo "${subdir} failed."
        else
            rm -r hpctoolkit-measurements
            rm -r hpctoolkit-database
        fi
        cd ..
    else
        echo "${subdir} skipped."
    fi
done
