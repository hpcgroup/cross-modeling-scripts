#!/usr/bin/env python3

from os.path import join as path_join
import glob
import json

root = '/usr/WS1/dnicho/summer2022/resource-equivalences/data/corona/laghos'

for subdir in glob.glob(path_join(root, '*', 'results.json')):
    print(subdir)
    data = json.load(open(subdir, 'r'))
    print(data['machine'])
    data['machine'] = 'corona'
    print(data['machine'])
    json.dump(data, open(subdir, 'w'))
