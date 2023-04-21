''' Dataset utilities.
    author: Daniel Nichols
'''

# tpl imports
import pandas as pd


def add_one_hot(df, column, drop=False):
    ''' Add one-hot-encoded columns to df based on column.
        Args:
            drop: If true, then drop `column` after encoding it.
    '''
    assert column in df.columns

    one_hot = pd.get_dummies(df[column])
    if drop:
        df = df.drop(column)
    df = df.join(one_hot)
    return df


def get_regression_dataset(df, relative_to='min', include_app=False, run_size='all', round_targets=False,
    include_runtime=None):
    ''' Build a dataset for regression. Regressor target is n-vector of relative
        performance across available systems.
        Args:
            relative_to: Can be 'min', 'max', None, or one of the system names.
                If min/max, then values are calculated relative to min/max of
                each sample. If None, then runtimes are left as-is. If a system
                name is provided, then values are calculated relative to that
                system.
            include_app: If true, then the application is included in feature
                vector one-hot-encoded.
            run_size: Either 'core', 'node', or 'all'. Use single core and/or
                single node profiling results.
            round_targets: If true, then round regressor targets to nearest
                integer.
            include_runtime: One of 'overhead', 'absolute', 'both', or None.
    '''
    assert run_size in ['core', 'node', 'all']
    assert include_runtime in ['overhead', 'absolute', 'both', None]

    # create copy of data
    df = df.copy(deep=True)

    # filter ranks
    if run_size == 'core':
        df = df[df['ranks'] == 1]
    elif run_size == 'node':
        raise NotImplementedError('node run_size filter not yet implemented.')
    else:
        pass

    # calculate overhead column if needed; do this before 'duration' is dropped
    if include_runtime in ['overhead', 'both']:
        df['Overhead'] = (df['duration']*60.0) - df['REALTIME (sec)']

    # remove meta-data columns and set index
    df = df[df['app'] == 'laghos']
    df.drop(['exec', 'modules', 'spack_env', 'exec_path', 'events', 'path', 'duration'], axis=1, inplace=True)
    df.set_index(['app', 'args', 'ranks', 'machine'], inplace=True)

    # show columns with na
    #print(df.columns[df.isna().any()].tolist())
    df.dropna(axis=1, inplace=True)

    # calculate performance relative to minimum across systems
    if relative_to in ['min', 'max']:
        rel = df['REALTIME (sec)'].groupby(['app', 'args', 'ranks']).agg(relative_to)
        df['Relative Time'] = df['REALTIME (sec)'] / rel
    else:
        rel = df.loc[:,:,:,relative_to]['REALTIME (sec)']
        df['Relative Time'] = df['REALTIME (sec)'] / rel
        #print(df['Relative Time'].values)

    #df[['REALTIME (sec)', 'Relative Time']].to_csv('times.csv')
    #exit(0)

    # expand relative times from each machine to columns; and add those columns to df
    pivot_df = pd.pivot(df.reset_index(), index=['app', 'args', 'ranks'], columns='machine', values='Relative Time')
    pivot_df.columns = pivot_df.columns + ' Relative Time'
    merged_df = df.merge(pivot_df, left_index=True, right_index=True, validate='1:1')

    # one-hot-encode machine column
    merged_df.reset_index(inplace=True)
    df = add_one_hot(merged_df, 'machine')
    df.drop('Relative Time', axis=1, inplace=True)
    df.set_index(['app', 'args', 'ranks', 'machine'], inplace=True)

    # remove absolute runtime column if requested
    if include_runtime in ['overhead', None]:
        df.drop('REALTIME (sec)', axis=1, inplace=True)

    # optionally encode application
    if include_app:
        df.reset_index(inplace=True)
        df = add_one_hot(df, 'app')
        df.set_index(['app', 'args', 'ranks', 'machine'], inplace=True)

    # optionally round target values
    if round_targets:
        target_cols = df.columns[df.columns.str.endswith('Relative Time')]
        df[target_cols] = df[target_cols].round(2).astype('float64')

    return df