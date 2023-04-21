''' Some simpler ML strategies on the data.
    author: Daniel Nichols
'''
# std imports
from argparse import ArgumentParser

# tpl imports
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, OrthogonalMatchingPursuit
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, explained_variance_score
from sklearn.model_selection import train_test_split, GridSearchCV, cross_validate
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from scipy.stats import rankdata
from xgboost import XGBRegressor

# local imports
from dataset import get_regression_dataset


# sklearn forces warnings -- ugh -- this should get rid of them though
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True, help='input dataset')
    parser.add_argument('-t', '--task', type=str, choices=['regression', 'classification'], default='regression',
        help='What training problem to run.')
    return parser.parse_args()


def get_dataset(fpath, task):
    df = pd.read_csv(fpath)

    if task == 'regression':
        return get_regression_dataset(df, round_targets=False, include_app=False, run_size='core',
            include_runtime=None, relative_to='quartz')
    else:
        raise NotImplementedError("training task {} not yet implemented.".format(task))

def split_features_labels(ds):
    LABEL_COLUMNS = ['quartz Relative Time', 'ruby Relative Time', 'corona Relative Time', 'lassen Relative Time']
    FEATURE_COLUMNS = list(set(ds.columns) - set(LABEL_COLUMNS))
    return ds[FEATURE_COLUMNS], ds[LABEL_COLUMNS]


def normalize(X):
    ''' normalize data set.
    '''
    BY_INST = ['FP_ARITH:SCALAR_DOUBLE', 'PAPI_BR_INS', 'FP_ARITH:SCALAR_SINGLE',
       'PAPI_SR_INS', 'ARITH', 'PAPI_LD_INS']
    for col in BY_INST:
        X[col] = X[col] / X['PAPI_TOT_INS']
    
    SCALE_COLS = ['PAPI_L2_LDM', 'PAPI_L2_STM', 'IO Bytes Read', 'IO Bytes Written',
       'PAPI_MEM_WCY', 'PAPI_L1_LDM', 'PAPI_L1_STM']
    if 'REALTIME (sec)' in X.columns:
        SCALE_COLS.append('REALTIME (sec)')
    if 'Overhead' in X.columns:
        SCALE_COLS.append('Overhead')
    X[SCALE_COLS] = StandardScaler().fit_transform(X[SCALE_COLS])
    return X


def same_order_score(y_true, y_pred):
    ''' Check how many elements share same ordering.
    '''
    same_order = lambda x: np.array_equal(rankdata(x[0]), rankdata(x[1]))
    total_same = sum(map(same_order, zip(y_true, y_pred)))
    return float(total_same) / y_pred.shape[0]


def regression_metrics(y_true, y_pred):
    ''' Return a dict of metrics based on y_true and y_pred results.
    '''
    return {
        'r2': r2_score(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'mae': mean_absolute_error(y_true, y_pred),
        'evs': explained_variance_score(y_true, y_pred),
        'sos': same_order_score(y_true, y_pred)
    }


def train_tree_regressor(ds):
    ''' Train a decision tree regressor on data set.
    '''
    X, y = split_features_labels(ds)
    #X = normalize(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    clf = DecisionTreeRegressor(max_depth=15)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    same_order_score(y_test, y_pred)

    scores = regression_metrics(y_test, y_pred)
    for metric, score in scores.items():
        print('{:3}: {:.3f}'.format(metric, score))


def get_regressor_best(Regressor, X, y, tune=None, **params):
    ''' Find an approximate best score from regressor on X and y.
    '''
    print('Training regressor \'{}\'...'.format(Regressor.__name__))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42, shuffle=True)
    rgrsr = Regressor(**params)
    best_score = 0
    scoring = 'neg_mean_absolute_error'

    if tune:
        search = GridSearchCV(rgrsr, tune, refit=True, scoring=scoring)
        search.fit(X_train, y_train)

        best_params = search.best_params_
        best_score = search.best_score_
        print('{} scores: {}\twith {}'.format(Regressor.__name__, -best_score, best_params))
        rgrsr = search.best_estimator_
    else:
        cv_results = cross_validate(rgrsr, X, y, cv=5, scoring=scoring)
        scores = cv_results['test_score']
        best_score = np.mean(scores)
        print('{} scores: {} +/- {}'.format(Regressor.__name__, -best_score, np.std(scores)))

        rgrsr.fit(X_train, y_train)
    
    if hasattr(rgrsr, 'feature_importances_'):
        if hasattr(rgrsr, 'feature_names_in_'):
            importances = sorted(zip(rgrsr.feature_names_in_, rgrsr.feature_importances_), key=lambda x: x[1], reverse=True)
            print('Feature Importances: {}'.format(importances))
        else:
            importances = sorted(zip(X.columns.tolist(), rgrsr.feature_importances_), key=lambda x: x[1], reverse=True)
            print('Feature Importances: {}'.format(importances))

    return rgrsr, best_score


def find_best_regressor(ds):
    ''' Try a large number of regressors and present the best one.
    '''
    X, y = split_features_labels(ds)
    X.reset_index(inplace=True, drop=True)
    y_orig = y
    y = y.reset_index(drop=True).to_numpy()
    X = normalize(X)
    models = []
    #print(X, y)

    #tune_params = {'fit_intercept': [True, False]}
    #result = get_regressor_best(LinearRegression, X, y, tune=tune_params)
    #models.append(result)

    #tune_params = {'max_depth': [1, 2, 4, 8, 12], 'criterion': ['mae', 'mse']}
    #result = get_regressor_best(DecisionTreeRegressor, X, y, tune=tune_params)
    #models.append(result)

    #tune_params = {'n_estimators': [10, 50, 100], 'criterion': ['mse', 'mae', 'poisson']}
    #result = get_regressor_best(RandomForestRegressor, X, y, tune=tune_params)
    #models.append(result)

    #tune_params = {'n_estimators': [10, 50, 100], 'criterion': ['mse', 'mae', 'poisson']}
    #result = get_regressor_best(ExtraTreesRegressor, X, y, tune=tune_params)
    #models.append(result)

    tune_params = {'n_estimators': [1,2,10,50,100], 'eta': [0.3, 0.1],
        'booster': ['gbtree', 'gblinear', 'dart']}
    result = get_regressor_best(XGBRegressor, X, y, tune=tune_params)
    models.append(result)

    #result = get_regressor_best(DummyRegressor, X, y, strategy='mean')
    #models.append(result)

    #result = get_regressor_best(DummyRegressor, X, y, strategy='median')
    #models.append(result)

    best_model, best_score = max(models, key=lambda x: x[1])
    print('\nSelecting \'{}\' as best model with score: {}'.format(best_model.__class__.__name__, -best_score))
    #_, X_test, _, y_test = train_test_split(X, y, test_size=0.1, random_state=42, shuffle=True)
    X_test, y_test = X[X['corona'] == 1], y_orig.loc[:,:,:,'corona'].to_numpy()
    y_true, y_pred = y_test, best_model.predict(X_test)
    scores = regression_metrics(y_true, y_pred)
    for metric, score in scores.items():
        print('{:3}: {:.3f}'.format(metric, score))

    print('\nExample Outputs:')
    print('Actual\t\t\tPredicted')
    print('------\t\t\t--------')
    LIM = 5
    for tr, pr in zip(y_true[:LIM], y_pred[:LIM]):
        tr_list, pr_list = ['{}'.format(x) for x in tr], ['{:0.4f}'.format(x) for x in pr]
        print('{} -> {}'.format(str(tr_list), str(pr_list)))

    
def main():
    args = get_args()

    ds = get_dataset(args.dataset, args.task)
    ds.dropna(inplace=True)
    
    find_best_regressor(ds)
    

if __name__ == '__main__':
    main()
