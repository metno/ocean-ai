#CODE FOR CREATING CORRELATION MATRICES

#Import necessary packages
import xarray as xr
import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sea
import numpy as np
import sys 
import argparse
import os 


def import_ds(filepath, Norkyst = False):
    print(f'Norkyst is {Norkyst}')
    if Norkyst == False:
        ds = xr.open_dataset(filepath).isel(time = 0) #For the resultfiles because they only have one layer 
        vars_keep = ['salinity_0', 'temperature_0', 'zeta', 'u_eastward_0', 'v_northward_0']
    else:
        ds = xr.open_dataset(filepath).isel(s_rho = -1)
        ds = ds.resample(time = '3H').mean(dim = 'time')
        ds = ds.isel(time = 0)
        vars_keep = ['salinity', 'temperature', 'zeta', 'u_eastward', 'v_northward']
    vars = list(ds.data_vars.keys())
    diff = list(filter(lambda i: i not in vars_keep, vars)) 
    dataset = ds.drop_vars(diff)
    print(f"All other variables removed. The variables dropped are: {diff}")
    return dataset

#Plotting the correlation matrix
def plot_corr(filepath, title, save_path, Norkyst = False):

    """
    This function takes in a filepath for .nc files and will make a correlation matrix for selected variables from the datafile. 
    The variables are selected when you run the code and you return a list of variables like: salinity, temperature etc. 

    Args:
    args[1] : Full path to the file you want to use. 
    args[2] : The title of the correlation matrix in the plot and the name of the file when being saved.
    args[3] : Full path to the chosen area to save the plot. It is saved as a png unless changed manually in the code. 
    args[4] : A boolean response to wether the dataset is a Norkyst dataset or not. This arg is optional and the default boolean response is False.
              If changed to True - the code will only select the surface layer of the Norkyst model.
    """

    dataset = import_ds(filepath, Norkyst = Norkyst)
    dataset_pd = dataset.to_dataframe()
    print(dataset_pd.head())
    if not Norkyst:
        vars_keep = ['salinity_0', 'temperature_0', 'zeta', 'u_eastward_0', 'v_northward_0']
        dataset_pd = dataset_pd[vars_keep]
        corr_matrix = dataset_pd.corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        fig, ax = plt.subplots(figsize=(12,10))
        cmap = sea.cubehelix_palette(230,20, as_cmap = True)
        sea.heatmap(corr_matrix, mask = mask, cmap = cmap, vmin= -1, vmax = 1, center = 0, square = True, linewidths = 0.5, cbar_kws={'shrink': 0.5}, annot = True)
        full_save = os.path.join(save_path, f'{title}.png')
        plt.title(f'{title}')
        fig.savefig(f'{full_save}')
        plt.show()
    else:
        vars_keep = ['salinity', 'temperature', 'zeta', 'u_eastward', 'v_northward']
        dataset_pd = dataset_pd[vars_keep]
        corr_matrix = dataset_pd.corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        fig, ax = plt.subplots(figsize=(12,10))
        cmap = sea.cubehelix_palette(230,20, as_cmap = True)
        sea.heatmap(corr_matrix, mask = mask, cmap = cmap, vmin= -1, vmax = 1, center = 0, square = True, linewidths = 0.5, cbar_kws={'shrink': 0.5}, annot = True)
        full_save = os.path.join(save_path, f'{title}.png')
        plt.title(f'{title}')
        fig.savefig(f'{full_save}')
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating correlation plots')
    parser.add_argument('filepath', metavar='Filepath to datafile', help='Please enter the full path')
    parser.add_argument('title', metavar='Title of the Correlation Matrix', help='Enter the title - for example specify which model you are using')
    parser.add_argument('save_path', metavar="Path to folder for saving pictures", help='Please enter the full path')
    parser.add_argument('--Norkyst', action='store_true', help='Set Norkyst = True if it is a Norkyst file to select out the surface layer', required=False)
    args = parser.parse_args()
    
    filepath = args.filepath 
    title_plot = args.title
    savefig_path = args.save_path
    Norkyst = args.Norkyst


#Trial run result files
"""
filepath = '/lustre/storeB/project/fou/hi/foccus/experiments/learning_rate/625e-3/inference/625_2d.nc'
title_plot = 'Learning rate: 625e-3 2D'
savefig_path = '/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures'
"""

#Trial run Norkyst for the same date
"""
filepath = '/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-20240502.nc'
title_plot = 'Norkyst Hindcast'
savefig_path = '/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures'
"""

plot_corr(filepath, title_plot, savefig_path, Norkyst)

#To save figs in Malenes folder
#/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures

