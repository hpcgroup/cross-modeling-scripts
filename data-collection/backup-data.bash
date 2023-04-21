#!/bin/bash
# Back up data to archive/tape storage on LC system.
# author: Daniel Nichols
# date: July 2022

# settings
data_dir="/usr/WS1/dnicho/summer2022/resource-equivalences/data"
output="/usr/WS1/dnicho/summer2022/resource-equivalences/data.bkp.tar.gz"

# create backup
#tar -czvf ${output} ${data_dir}
#htar -cvf data.bkp.tar ${data_dir}
tar -cf - -C ${data_dir} . | pv -s $(du -sb ${data_dir} | awk '{print $1}') | gzip > ${output}

