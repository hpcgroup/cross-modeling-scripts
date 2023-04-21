# Cross Modeling

### Collecting Dataset
To collect a data set for a single *system* and *app* pair use the 
`analysis/collect-dataset.py` script. You can run it as

```bash
python3 collect-dataset.py --root ../data/<system_name>/<app_name>/ --output <output_csv>

# for instance
python3 collect-dataset.py --root ../data/quartz/laghos --output ../data/quartz/laghos/data.csv
```

This will build a csv combining the results for all the *quartz* *laghos* runs.
This script will also tell you if any of the runs failed or produced other weird
outputs. You can add the `--clean` flag to have it remove bad results 
directories. To combine all of the datasets use `analysis/combine-datasets.py`.
This can be run as

```bash
python3 combine-datasets.py -v --root ../data --output ../data/data.csv
```

This will combine all of the datasets into a single csv file.

### Backing Up
Another helper script is `data-collection/backup-data.bash`. It will produce
a zipped tar file with all the data in it. You can also uncomment the *htar*
line to get it to save to taped archives. Simply run `bash backup-data.bash` 
and it will produce `data.bkp.tar.gz`.


### Workflow
To collect data I ran the following steps:

```bash

# Run collect-dataset.py for each system/app pair
cd analysis
python3 collect-dataset.py --root ... --output ...

# Combine
python3 combine-datasets.py -v --root ../data --output ../data/data.csv

# And finally backup
cd ../data-collection
bash backup-data.bash
```
