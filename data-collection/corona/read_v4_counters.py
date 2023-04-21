#!/usr/bin/env python3

from argparse import ArgumentParser
from os.path import join as path_join
import json

from pathlib import Path
from hpctoolkit.formats.v4.profiledb import ProfileDB
from hpctoolkit.formats.v4.cctdb import ContextDB
from hpctoolkit.formats.v4.metadb import MetaDB


parser = ArgumentParser()
parser.add_argument('-i', '--input', required=True, type=str, help='input hpctoolkit db path')
parser.add_argument('-a', '--append', type=str, help='existing results json to append to')
args = parser.parse_args()


prof_db = ProfileDB.from_file(open(path_join(args.input, "profile.db"), 'rb'))
meta_db = MetaDB.from_file(open(path_join(args.input, "meta.db"), 'rb'))
cct_db = ContextDB.from_file(open(path_join(args.input, "cct.db"), 'rb'))

cct_db._with(meta=meta_db, profile=prof_db)
prof_db._with(meta=meta_db)

# find node 0, rank 0 -- profile
def get_id(id_tuple, key):
    if id_tuple is None:
        return None
    for id in id_tuple.ids:
        if id._kindstr == key:
            return id.logical_id
    return None

main_profile = [prof for prof in prof_db.profile_infos.profiles if hasattr(prof, "id_tuple") and get_id(prof.id_tuple, "RANK") == 0 and get_id(prof.id_tuple, "THREAD") == 0][0]

# get Context of main function in CCT
for entry_point in meta_db.context.entry_points:
    to_visit = list(entry_point.children)
    while len(to_visit) > 0:
        c = to_visit.pop(0)
        if c.function and c.function.name == "main":
            main_context = c
        to_visit.extend(c.children)


# match metrics with counter values
counter_values = main_profile.values[main_context.ctx_id]
counters = {}

for metric in meta_db.metrics.metrics:
    name = metric.name
    matches = [s for s in metric.summaries if s.stat_metric_id in counter_values]
    if len(matches) > 0:
        counters[name] = counter_values[matches[0].stat_metric_id]


# init data dict
results = {}
if args.append:
    with open(args.append, 'r') as fp:
        results = json.load(fp)

results.update(counters)
if args.append:
    with open(args.append, 'w') as fp:
        json.dump(results, fp)
else:
    print(counters)
