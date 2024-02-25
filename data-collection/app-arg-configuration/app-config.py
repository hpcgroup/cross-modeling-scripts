from arg_gen import Arg

class App:
    
    def __init__(self, name: str):
        # assert name in ['laghos', 'kripke', 'lulesh', 'minivite', 'self.argsbench', 'minife']
        self.arg = Arg()
        self.name = name
        if name == 'laghos':
            self.add_laghos_args()
        elif name == 'kripke':
            self.add_kripke_args()
        elif name == 'lulesh':
            self.add_lulesh_args()
        elif name == 'minivite':
            self.add_minivite_args()
        elif name == 'xsbench':
            self.add_xsbench_args()
        elif name == 'minife':
            self.add_minife_args()
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
                    f.write('"{}"\n'.format(x))
                print('Generated {} args.'.format(count))

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
        self.arg.add_choices('-s', ['small', 'large', 'self.argL', 'self.argself.argL'])
        self.arg.add_choices('-G', ['unionized', 'nuclide', 'hash'])

    def add_minife_args(self):
        self.arg.add_range('-nself.arg', 50, 200, 25)
        self.arg.add_range('-ny', 50, 200, 25)
        self.arg.add_range('-nz', 50, 200, 25)

apps = ['laghos', 'kripke', 'lulesh', 'minivite', 'xsbench', 'minife']
output_folder = 'configs'
for app in apps:
    a = App(app)
    a.write(output_folder)