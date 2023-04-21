''' Generate a combination of input args.
    author: Daniel Nichols
'''
# std imports
from itertools import product
import re

# tpl imports
import numpy as np


def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

class Arg:
    def __init__(self):
        self.keys, self.vals = [], []

    def add_range(self, key, a, b, step):
        assert key not in self.keys

        self.keys.append(key)
        self.vals.append(list(np.arange(a, b, step)))
    
    def add_choices(self, key, choices):
        assert key not in self.keys

        self.keys.append(key)
        self.vals.append(choices)

    def add_binary(self, key):
        self.add_choices(f'<empty-{key}>', ['', key])
    
    def arg_list(self):
        for x in product(*self.vals):
            x_str = ['{:g}'.format(y) if is_number(y) else y for y in x]
            arg_str = ' '.join( sum(zip(self.keys, x_str), ()) )
            arg_str = re.sub('<empty-[-\w]+>', '', arg_str)
            arg_str = re.sub(' +', ' ', arg_str)
            yield arg_str.strip()



def add_laghos_args(x):
    x.add_choices('-p', [1, 2, 3])
    x.add_choices('-dim', [2, 3])
    x.add_choices('-rs', [1, 2, 3])
    x.add_range('-tf', 3.0, 6.0, 0.5)
    x.add_choices('', ['', '-pa'])


def add_kripke_args(x):
    x.add_choices('--niter', [5, 10, 15])
    x.add_choices('--pmethod', ['sweep', 'bj'])
    x.add_choices('--groups', [8, 16, 32])
    x.add_choices('--arch', ['sequential'])
    x.add_choices('--legendre', [0, 1, 2, 3, 4])

def add_lulesh_args(x):
    x.add_range('-i', 5, 30, 5)
    x.add_range('-s', 30, 65, 5)

def add_minivite_args(x):
    x.add_binary('-w')
    x.add_binary('-l')
    x.add_range('-p', 1, 10, 1)
    #x.add_choices('-n', [32, 64, 128, 256, 512])
    x.add_choices('-n', [4096, 8192, 16384])


def add_xsbench_args(x):
    x.add_choices('-t', [1, 32])
    x.add_choices('-m', ['history', 'event'])
    x.add_choices('-s', ['small', 'large', 'XL', 'XXL'])
    x.add_choices('-G', ['unionized', 'nuclide', 'hash'])


def add_minife_args(x):
    x.add_range('-nx', 50, 200, 25)
    x.add_range('-ny', 50, 200, 25)
    x.add_range('-nz', 50, 200, 25)


arglist = Arg()
#add_laghos_args(arglist)
#add_kripke_args(arglist)
#add_lulesh_args(arglist)
#add_minivite_args(arglist)
#add_xsbench_args(arglist)
add_minife_args(arglist)

count = 0
for x in arglist.arg_list():
    count += 1
    print('"{}"'.format(x))

print('Generated {} args.'.format(count))