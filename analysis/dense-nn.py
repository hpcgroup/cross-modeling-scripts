''' Try the training problem with a dense-nn.
    author: Daniel Nichols
    date: August 2022
'''
# std imports
from argparse import ArgumentParser

# tpl imports
from alive_progress import alive_it
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data_utils
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

# local imports
from dataset import get_regression_dataset


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True, help='input dataset')
    parser.add_argument('-t', '--task', type=str, choices=['regression', 'classification'], default='regression',
        help='What training problem to run.')
    parser.add_argument('--hidden-sizes', type=int, nargs='+', default=[128], help='size of hidden layers')
    parser.add_argument('--batch-size', type=int, default=4, help='training batch size')
    parser.add_argument('--epochs', type=int, default=5, help='# of training epochs')
    return parser.parse_args()


def normalize(X):
    ''' normalize data set.
    '''
    from sklearn.preprocessing import StandardScaler
    return StandardScaler().fit_transform(X)


def same_order_score(y_true, y_pred):
    ''' Check how many elements share same ordering.
    '''
    from scipy.stats import rankdata
    same_order = lambda x: np.array_equal(rankdata(x[0]), rankdata(x[1]))
    total_same = sum(map(same_order, zip(y_true, y_pred)))
    return float(total_same) / y_pred.shape[0]


def regression_metrics(y_true, y_pred):
    ''' Return a dict of metrics based on y_true and y_pred results.
    '''
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, explained_variance_score
    return {
        'r2': r2_score(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'mae': mean_absolute_error(y_true, y_pred),
        'evs': explained_variance_score(y_true, y_pred),
        'sos': same_order_score(y_true, y_pred)
    }


class Net(nn.Module):
    def __init__(self, hidden_sizes=(128, 64)):
        super(Net, self).__init__()

        self.fc_layers_ = nn.Sequential(*[nn.LazyLinear(hs) for hs in hidden_sizes])

    def forward(self, x):
        for layer in self.fc_layers_[:-1]:
            x = F.relu( layer(x) )
        
        x = self.fc_layers_[-1](x)
        return x


def train_regression(ds, model, learning_rate=0.001, epochs=5):
    criterion = nn.L1Loss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):

        running_loss, total_loss = 0.0, 0.0
        bar = alive_it(ds, title='Epoch {}'.format(epoch), force_tty=True, theme='smooth', receipt=True, receipt_text=True)
        for idx, (inputs, targets) in enumerate(bar, 0):

            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            total_loss = running_loss / (idx + 1)
            bar.text = 'Loss: {:.3f}'.format(total_loss)


    print('\nExample Outputs:')
    print('Actual\t\t\tPredicted')
    print('------\t\t\t--------')
    LIM = 50
    y_true, y_pred = [], []
    for _ in range(LIM // ds.batch_size):
        batch, actual = iter(ds).next()
        predicted = model(batch).detach()
        batch, predicted = batch.numpy(), predicted.numpy()
        y_true.append(actual)
        y_pred.append(predicted)

        for tr, pr in zip(actual, predicted):
            tr_list, pr_list = ['{:0.4f}'.format(x) for x in tr], ['{:0.4f}'.format(x) for x in pr]
            print('{} -> {}'.format(str(tr_list), str(pr_list)))
    
    y_true = np.concatenate(y_true)
    y_pred = np.concatenate(y_pred)
    scores = regression_metrics(y_true, y_pred)
    print()
    for metric, score in scores.items():
        print('{:3}: {:.3f}'.format(metric, score))


def main():
    args = get_args()

    df = pd.read_csv(args.dataset)
    df = get_regression_dataset(df, relative_to='min', include_app=False, run_size='core',
        round_targets=False, include_runtime='both')
    df.dropna(inplace=True)

    TARGETS = ['quartz Relative Time', 'ruby Relative Time']
    FEATURES = list(set(df.columns) - set(TARGETS))
    ds = data_utils.TensorDataset(
        torch.tensor(normalize(df[FEATURES].values)).float(), 
        torch.tensor(df[TARGETS].values).float())
    dl = data_utils.DataLoader(ds, batch_size=args.batch_size, shuffle=True)

    model = Net(args.hidden_sizes)

    train_regression(dl, model, epochs=args.epochs)



if __name__ == '__main__':
    main()