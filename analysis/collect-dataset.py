'''
author: Daniel Nichols
date: June 2022
'''
# std imports
from argparse import ArgumentParser
from os import listdir
from os.path import exists, isdir, join as path_join
from shutil import rmtree
import json
from csv import QUOTE_NONNUMERIC

# tpl imports
from alive_progress import alive_it
import pandas as pd


def parse_args():
    ''' Parses input arguments
    '''
    parser = ArgumentParser()
    parser.add_argument('-c', '--configuration', help='json file containing run configuration')
    parser.add_argument('--root', type=str, required=True, help='root to data set')
    parser.add_argument('-o', '--output', type=str, help='output dataset file path')
    parser.add_argument('--clean', action='store_true', help='cleans up data directory ' +
        '(removes invalid dirs)')
    return parser.parse_args()


def get_input_to_failed_job(dirpath):
    ''' Recover the input arguments to a failed run. The 'results.json' file may
        be ill-formatted.
    '''
    input_args = ''
    with open(path_join(dirpath, 'results.json'), 'r') as fp:
        try:
            obj = json.load(fp)
            input_args = obj['args']
        except json.JSONDecodeError:
            start_str = '\t"args": "'
            fp.seek(0)
            for line in fp:
                if line.startswith(start_str):
                    input_args = line[len(start_str):-3]
                    break
    return input_args


def check_seg_fault(dirpath):
    ''' When a run segfaults it creates a huge stderr output. Identify these and denote
        what input led to segfault.
    '''
    segfault = False
    with open(path_join(dirpath, 'std.err'), 'r') as fp:
        for line in fp:
            if 'Segmentation fault (signal 11)' in line:
                segfault = True
                break
        
    if segfault:
        input_args = get_input_to_failed_job(dirpath)
        print('Profile at \'{}\' segfaulted on input \'{}\'.'.format(dirpath.split('/')[-1], input_args))
    
    return segfault
    

def check_time_limit(dirpath):
    ''' Check if job failed cause of time limit.
    '''
    ran_out_of_time = False
    with open(path_join(dirpath, 'std.err'), 'r') as fp:
        for line in fp:
            if line.strip().endswith('DUE TO TIME LIMIT ***'):
                ran_out_of_time = True
                break

        if ran_out_of_time:
            input_args = get_input_to_failed_job(dirpath)
            print('Profile at \'{}\' ran out of time on input \'{}\'.'.format(
                dirpath.split('/')[-1], input_args
            ))

    return ran_out_of_time


def run_errored_cleanly(dirpath):
    ''' Check if the run errored cleanly.
    '''
    errored = False
    with open(path_join(dirpath, 'std.err'), 'r') as fp:
        for line in fp:
            if line.strip() == 'FileNotFoundError: [Errno 2] No such file or directory: \'hpctoolkit-database/experiment.xml\'':
                errored = True
                break
    
    with open(path_join(dirpath, 'std.out'), 'r') as fp:
        for line in fp:
            # hpctoolkit build-db error
            if line.strip().startswith('ERROR: [Diagnostics::FatalException] Error:'):
                errored = True
                break
        
    if errored:
        input_args = get_input_to_failed_job(dirpath)
        print('Profile at \'{}\' errored during run on input \'{}\'.'.format(
            dirpath.split('/')[-1], input_args
        ))
    return errored
            

def is_valid_results_dir(dirpath):
    ''' Checks if `dirpath` points to a valid results directory. i.e. does it 
        exist and is the data in the correct format.
    '''
    if not isdir(dirpath):
        return False

    files = listdir(dirpath)
    EXPECTED = ['std.out', 'std.err', 'results.json']
    UNEXPECTED = ['hpctoolkit-database', 'hpctoolkit-measurements']
    #UNEXPECTED = ['hpctoolkit-measurements']

    has_all_files = all([fname in files for fname in EXPECTED])
    if not has_all_files:   # early exit
        return False

    has_no_invalid_files = all([fname not in files for fname in UNEXPECTED])
    if not has_no_invalid_files:   # early exit
        input_args = get_input_to_failed_job(dirpath)
        print(f'Profile at \'{dirpath.split("/")[-1]}\' ran out of time on input \'{input_args}\'.')
        return False

    has_valid_results_json = True
    try:
        json.load(open(path_join(dirpath, 'results.json')))
    except ValueError:
        has_valid_results_json = False
    if not has_valid_results_json:   # early exit
        return False

    did_not_segfault = not check_seg_fault(dirpath)
    if not did_not_segfault:   # early exit
        return False

    did_not_run_out_of_time = not check_time_limit(dirpath)
    if not did_not_run_out_of_time:   # early exit
        return False

    did_not_error_cleanly = not run_errored_cleanly(dirpath)
    if not did_not_error_cleanly:   # early exit
        return False

    return all([has_all_files, has_no_invalid_files, has_valid_results_json, did_not_segfault, did_not_run_out_of_time,
        did_not_error_cleanly])


def get_run_results(root, clean=False):
    ''' Collect all the run directories within a root. Returns a dataframe with 
        the corresponding results.
    '''
    subdirs = listdir(root)
    FILES_TO_IGNORE = ['data.csv']

    valid_count = 0
    total_count = sum([isdir(path_join(root, x)) for x in subdirs])
    results_data = []
    for subdir in alive_it(subdirs, bar='classic', spinner='classic'):
        if subdir in FILES_TO_IGNORE or len(listdir(path_join(root, subdir))) == 0:
            continue
        
        #check validity of data directory
        is_valid = is_valid_results_dir(path_join(root, subdir))
        if not is_valid:
            print('\'{}\' is an invalid results directory.'.format(subdir))
            if clean and isdir(path_join(root, subdir)):
                print('Removing \'{}\'...'.format(path_join(root, subdir)))
                rmtree(path_join(root, subdir))
            continue

        valid_count += 1
        result = {}

        with open(path_join(root, subdir, 'results.json')) as fp:
            tmp_result = json.load(fp)
            result.update(tmp_result)
        
        results_data.append(result)

    df = pd.DataFrame(results_data)
    df['duration'] = pd.to_numeric(df['duration']) # string -> number

    print('Parsed {} directories. {} / {} valid.'.format(total_count, valid_count, total_count))

    # group rows with the same column
    # agg columns: counters (...), events (cat), path (list), duration (avg)
    group_columns = ['machine', 'app', 'exec', 'args', 'ranks', 'modules', 'spack_env', 'exec_path']
    agg_funcs = {'events': ' '.join, 'path': list, 'duration': 'min'}
    agg_funcs.update( dict.fromkeys(df.columns[df.dtypes.eq('float64')], 'first') )
    group_df = df.groupby(by=group_columns).agg(agg_funcs).reset_index()

    return group_df


def main():
    args = parse_args()

    df = get_run_results(args.root, clean=args.clean)

    if args.output:
        df.to_csv(args.output, index=False, quoting=QUOTE_NONNUMERIC)
        print('Wrote dataset with {} rows.'.format(df.shape[0]))



if __name__ == '__main__':
    main()