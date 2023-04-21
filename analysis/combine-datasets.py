# Combine a set of data sets into a unified dataset
# author: Daniel Nichols
# date: July 2022

# std imports
from argparse import ArgumentParser
from glob import glob
from os.path import join as path_join
from os import sep as FILE_SEPARATOR
from csv import QUOTE_NONNUMERIC

# tpl imports
import pandas as pd


def vprint(verbose, msg, **kwargs):
    if verbose:
        print(msg, **kwargs)

'''
PAPI_BR_INS,PAPI_LD_INS,PAPI_SR_INS,PAPI_TOT_INS,PAPI_L1_LDM,PAPI_L1_STM,PAPI_L2_LDM,
PAPI_L2_STM,EPT,FP_ARITH:SCALAR_SINGLE,FP_ARITH:SCALAR_DOUBLE,ARITH,IO Bytes Read,IO Bytes Written,
PAPI_MEM_WCY,REALTIME (sec)
'''

'''
~PAPI_BR_INS ~PAPI_TOT_INS
amd64_fam17h_zen2::LS_DISPATCH:STORE_DISPATCH amd64_fam17h_zen2::LS_DISPATCH:LD_DISPATCH
perf::L1-DCACHE-LOAD-MISSES perf::L1-ICACHE-LOAD-MISSES
perf::STALLED-CYCLES-FRONTEND perf::STALLED-CYCLES-BACKEND 
IO REALTIME
gpu=amd
'''


'''
perf::BRANCH-INSTRUCTIONS power9::PM_LD_CMPL power9::PM_ST_CMPL perf::INSTRUCTIONS
power9::PM_LD_MISS_L1 power9::PM_ST_MISS_L1 power9::PM_L2_ST_MISS power9::PM_L2_LD_MISS
PAPI_INT_INS
PAPI_FP_INS
perf::STALLED-CYCLES-FRONTEND perf::STALLED-CYCLES-BACKEND
IO REALTIME
gpu=nvidia
'''

def get_unique_col(df, col='machine'):
    ''' get machine from dataframe '''
    vals = df[col].unique()
    assert len(vals) == 1
    return str(vals[0])


def normalize_columns(df):
    ''' Some of the counter columns are the same thing but have different names
        on different systems. i.e. clx::ARITH and bdw_ep::ARITH represent the
        same counter on Ruby and Quartz, respectively. This will adjust the 
        column names to fix this in `df`. Changes columns in-place.
    '''
    CUR_MACHINE = get_unique_col(df, col='machine')

    # remove system specific prefixes
    SYSTEM_PREFIXES = ['clx::', 'bdw_ep::']
    for pref in SYSTEM_PREFIXES:
        df.columns = df.columns.str.replace(pref, '', n=1, regex=False)

    # remove trailing whitespace
    df.columns = df.columns.str.rstrip()

    if CUR_MACHINE == 'corona':
        df['PAPI_MEM_WCY'] = df['perf::STALLED-CYCLES-FRONTEND'] + df['perf::STALLED-CYCLES-BACKEND']
        df['PAPI_L1_LDM'] = df['perf::L1-DCACHE-LOAD-MISSES'] + df['perf::L1-ICACHE-LOAD-MISSES']
        for col in ['PAPI_L1_STM','PAPI_L2_LDM','PAPI_L2_STM','EPT','FP_ARITH:SCALAR_SINGLE','FP_ARITH:SCALAR_DOUBLE','ARITH']:
            df[col] = -1
        df.drop(columns=['perf::STALLED-CYCLES-FRONTEND', 'perf::STALLED-CYCLES-BACKEND', 'perf::L1-DCACHE-LOAD-MISSES', 'perf::L1-ICACHE-LOAD-MISSES'], inplace=True)
        
    if CUR_MACHINE == 'lassen':
        df['PAPI_MEM_WCY'] = df['perf::STALLED-CYCLES-FRONTEND'] + df['perf::STALLED-CYCLES-BACKEND']
        df['EPT'] = -1
        df['FP_ARITH:SCALAR_SINGLE'] = -1
        df.drop(columns=['perf::STALLED-CYCLES-FRONTEND', 'perf::STALLED-CYCLES-BACKEND'], inplace=True)

    column_map = {
        'amd64_fam17h_zen2::LS_DISPATCH:STORE_DISPATCH': 'PAPI_SR_INS',
        'amd64_fam17h_zen2::LS_DISPATCH:LD_DISPATCH': 'PAPI_LD_INS',
        'perf::BRANCH-INSTRUCTIONS': 'PAPI_BR_INS',
        'power9::PM_LD_CMPL': 'PAPI_LD_INS',
        'power9::PM_ST_CMPL': 'PAPI_SR_INS',
        'perf::INSTRUCTIONS': 'PAPI_TOT_INS',
        'power9::PM_LD_MISS_L1': 'PAPI_L1_LDM',
        'power9::PM_ST_MISS_L1': 'PAPI_L1_STM', 
        'power9::PM_L2_ST_MISS': 'PAPI_L2_STM', 
        'power9::PM_L2_LD_MISS': 'PAPI_L2_LDM',
        'PAPI_FP_INS': 'FP_ARITH:SCALAR_DOUBLE',
        'PAPI_INT_INS': 'ARITH',
        }
    df.rename(columns=column_map, inplace=True)


def normalize_inputs(df):
    MACHINE = get_unique_col(df, col='machine')
    APP = get_unique_col(df, col='app')
    
    if APP == 'laghos':
        if MACHINE == 'corona':
            df['args'] = df['args'].str.replace(r'-d hip', '')
        elif MACHINE == 'lassen':
            df['args'] = df['args'].str.replace(r'-d cuda', '')
        df['args'] = df['args'].str.strip()



def combine_datasets(datadir, verbose=False):
    ''' combines data sets in datadir. Assumes datadir is formatted as 
        "datadir/<system>/<app>/data.csv". Each of these csv's will be concatenated together. 
    '''
    search_glob = path_join(datadir, '**', '**', 'data.csv')

    dataframes = []
    for fpath in glob(search_glob):
        path_parts = fpath.split(FILE_SEPARATOR)
        system, app = path_parts[-3], path_parts[-2]

        df = pd.read_csv(fpath)
        normalize_columns(df)
        normalize_inputs(df)
        dataframes.append(df)

        vprint(verbose, 'Collected dataset for \'{}\' on \'{}\'.'.format(app, system))
    
    combined = pd.concat(dataframes, ignore_index=True)
    vprint(verbose, 'Combined datasets.')
    vprint(verbose, 'Final dataset has {} rows and {} columns.'.format(combined.shape[0], combined.shape[1]))
    return combined


def main():
    parser = ArgumentParser()
    parser.add_argument('-r', '--root', required=True, type=str, help='root of data directories')
    parser.add_argument('-o', '--output', type=str, help='output csv file')
    parser.add_argument('-v', '--verbose', action='store_true', help='turn on verbose')
    args = parser.parse_args()

    df = combine_datasets(args.root, verbose=args.verbose)

    if args.output:
        df.to_csv(args.output, index=False, quoting=QUOTE_NONNUMERIC)
        vprint(args.verbose, 'Wrote combined dataset to \'{}\'.'.format(args.output))



if __name__ == '__main__':
    main()
