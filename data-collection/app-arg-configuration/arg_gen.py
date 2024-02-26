''' Generate a combination of input args.
    author: Daniel Nichols
'''
# std imports
from itertools import product
from typing import List
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
        self.keys, self.vals = {}, {}
    
    def add_procs(self, procs: List[int]):
        # added = 0
        # num_init = len(self.keys)
        for p in procs:
            if not p in self.keys:
                self.keys[p] = []
                self.vals[p] = []
                # added += 1
        


    def add_range(self, key, a, b, step, procs = [1, 32]):
        self.add_procs(procs)
        for p in procs:
            assert key not in self.keys[p]

            self.keys[p].append(key)
            self.vals[p].append(list(np.arange(a, b, step)))
    
    def add_choices(self, key, choices, procs = [1, 32]):
        self.add_procs(procs)
        for p in procs:
            assert key not in self.keys[p]

            self.keys[p].append(key)
            self.vals[p].append(choices)

    def add_binary(self, key, procs = [1, 32]):
        self.add_choices(f'<empty-{key}>', ['', key], procs)
    
    def arg_list(self, proc = 1):
        assert proc in self.keys
        keys = self.keys[proc]
        vals = self.vals[proc]
        for x in product(*vals):
            x_str = ['{:g}'.format(y) if is_number(y) else y for y in x]
            arg_str = ' '.join( sum(zip(keys, x_str), ()) )
            arg_str = re.sub('<empty-[-\w]+>', '', arg_str)
            arg_str = re.sub(' +', ' ', arg_str)
            yield arg_str.strip()

class App:
    
    def __init__(self, name: str):
        # assert name in ['laghos', 'kripke', 'lulesh', 'minivite', 'self.argsbench', 'minife']
        self.arg = Arg()
        self.name = name
        if name == 'laghos':
            self.add_laghos_args()
        elif name == 'kripke':
            self.add_kripke_args()
        elif name == 'lulesh2.0':
            self.add_lulesh_args()
        elif name == 'minivite':
            self.add_minivite_args()
        elif name == 'xsbench':
            self.add_xsbench_args()
        elif name == 'minife':
            self.add_minife_args()
        elif name == 'amg':
            self.add_amg_args()
        elif name == 'halo3d' or name == 'halo3d-26':
            self.add_halo3d_args()
        elif name == 'incast':
            self.add_incast_args()
        else:
            raise ValueError(f'Unknown app name: {name}')
        
        
    def write(self, folder: str):
        for p in self.arg.keys:
            file_name = f'{folder}/{self.name}-{p}.txt'
            with open(file_name, 'w') as f:
                print(f'App: {self.name} Num processors: {p}') 
                f.write(self.name + '\n')
                f.write('{}\n'.format(p))   
                count = 0
                for x in self.arg.arg_list(proc=p):
                    count += 1
                    f.write('{}\n'.format(x))
                print('Generated {} args.'.format(count))
    
    def add_amg_args(self):
        # for 1 processor
        self.arg.add_choices('-problem', [2], procs = [1])
        self.arg.add_choices('-P', ['1 1 1'], procs = [1])
        self.arg.add_choices('-n', ['256 256 256', '128 128 128', '64 64 64', '32 32 32', '16 16 16','8 8 8'], procs = [1])
        # for 32 ranks
        self.arg.add_choices('-problem', [1, 2], procs = [32])
        self.arg.add_choices('-P', ['2 2 1', '4 4 2'], procs = [32])
        self.arg.add_choices('-n', ['8 8 4', '16 16 8', '32 32 16', '64 64 32', '128 128 64'], procs = [32])

    def add_halo3d_args(self):
        self.arg.add_choices('-nx', [10, 15, 20, 25])
        self.arg.add_choices('-ny', [10, 15, 20, 25])
        self.arg.add_choices('-nz', [10, 15, 20, 25])
        self.arg.add_choices('-iterations', [50, 100])
        
        self.arg.add_choices('-pex', [1], procs=[1])
        self.arg.add_choices('-pey', [1], procs=[1])
        self.arg.add_choices('-pez', [1], procs=[1])

        self.arg.add_choices('-pex', [4], procs=[32])
        self.arg.add_choices('-pey', [4], procs=[32])
        self.arg.add_choices('-pez', [2], procs=[32])
        
    def add_incast_args(self):
        self.arg.add_range('-iterations', 1, 11, 1)
        self.arg.add_choices('-msgsize', [512, 1024, 2048])

    # def add_swfft_args(self):
    #     self.arg.add_range('-iterations', 1, 11, 1)

    def add_laghos_args(self):
        self.arg.add_choices('-p', [1, 2, 3])
        self.arg.add_choices('-dim', [2, 3])
        self.arg.add_choices('-rs', [1, 2, 3])
        self.arg.add_range('-tf', 3.0, 6.0, 0.5)
        self.arg.add_choices('', ['', '-pa'])

    def add_kripke_args(self):
        self.arg.add_choices('--niter', [5, 10, 15])
        self.arg.add_choices('--pmethod', ['sweep', 'bj'])
        self.arg.add_choices('--groups', [8, 16, 32])
        self.arg.add_choices('--arch', ['sequential'])
        self.arg.add_choices('--legendre', [0, 1, 2, 3, 4])

    def add_lulesh_args(self):
        self.arg.add_range('-i', 5, 30, 5)
        self.arg.add_range('-s', 30, 65, 5)

    def add_minivite_args(self):
        self.arg.add_binary('-w')
        self.arg.add_binary('-l')
        self.arg.add_range('-p', 1, 10, 1)
        self.arg.add_choices('-n', [32, 64, 128, 256, 512], procs=[1])
        self.arg.add_choices('-n', [4096, 8192, 16384], procs=[32])

    def add_xsbench_args(self):
        self.arg.add_choices('-t', [1, 32])
        self.arg.add_choices('-m', ['history', 'event'])
        self.arg.add_choices('-s', ['small', 'large', 'xL', 'xxL'])
        self.arg.add_choices('-G', ['unionized', 'nuclide', 'hash'])

    def add_minife_args(self):
        self.arg.add_range('-nself.arg', 50, 200, 25)
        self.arg.add_range('-ny', 50, 200, 25)
        self.arg.add_range('-nz', 50, 200, 25)

# apps = ['laghos', 'kripke', 'lulesh2.0', 'minivite', 'xsbench', 'minife']
apps = ['laghos', 'lulesh2.0', 'minivite', 'minife', 'halo3d-26', 'halo3d', 'amg', 'incast']
output_folder = 'configs'
for app in apps:
    a = App(app)
    a.write(output_folder)

# arglist = Arg()
# #add_laghos_args(arglist)
# #add_kripke_args(arglist)
# #add_lulesh_args(arglist)
# add_minivite_args(arglist)
# #add_xsbench_args(arglist)
# add_minife_args(arglist)
# for p in arglist.keys:
#     print('Num processors: {}'.format(p))    
#     count = 0
#     for x in arglist.arg_list(proc=p):
#         count += 1
#         print('"{}"'.format(x))
#     print('Generated {} args.'.format(count))
