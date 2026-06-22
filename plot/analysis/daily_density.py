import numpy as np 
import matplotlib.pyplot as plt 
import xarray as xr 
%pip install gsw
import gsw
from dataloader import open_dataset


def gen_files(checkpoint_norkyst, checkpoint_avg, surface = None): 
    filepath_norkyst = '/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024'
    file_path_avg = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages'

    vars_keep = ['salinity', 'temperature', 'height', 'latitude', 'zeta']
    norkyst = open_dataset(f'{filepath_norkyst}/{checkpoint_norkyst}')

    ds_clim = xr.open_dataset(f'{file_path_avg}/{checkpoint_avg}')

    for ds in [norkyst, ds_clim]:
        vars = list(ds.data_vars.keys())
        diff = list(filter(lambda i: i not in vars_keep, vars)) 
        dataset = ds.drop_vars(diff)
        print(f"All other variables removed. The variables dropped are: {diff}")







    


