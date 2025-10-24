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


#importing the dataset and selecting which variables to run the correlation matrix for the results
def import_ds(filepath):
    #Importing the dataset
    ds = xr.open_dataset(filepath)#.isel(s_rho = -1)
    #Printing out a list of the variables in the dataset to easily see and select which variables one wishes to create correlation matrix for
    vars = list(ds.data_vars.keys())
    print(vars)
    return ds 

#New function to interact with user. From the first function - the user gets a list of all variables to select from.
#The user provides a list of variables (example: salinity, temperature) and the rest are dropped in the sel_vars function
def sel_vars(filepath):
    ds = import_ds(filepath)
    user_input = input('Please provide a list of the variables you want to use seperated with commas:')
    #Strip to make the user input easy to process
    vars_keep = [var.strip() for var in user_input.split(',')]
    vars = list(ds.data_vars.keys())
    #Filtering out the variables from vars keep and removing them from vars
    diff = list(filter(lambda i: i not in vars_keep, vars)) 
    #Dropping non-selected variables
    dataset = ds.drop_vars(diff)
    print(f"All other variables removed. The variables dropped are: {diff}")
    return dataset

#Plotting the correlation matrix
def plot_corr(filepath, title, save_path):
    dataset = sel_vars(filepath)
    #convert dataset from xarray to pandas to use built-in function
    dataset_pd = dataset.to_dataframe()
    #Check if everything works as it should 
    print(dataset_pd.head())
    #Make correlation matrix 
    corr_matrix = dataset_pd.corr()
    #Make the matrix diagonal 
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    #Plot it 
    fig, ax = plt.subplots(figsize=(12,10))
    cmap = sea.cubehelix_palette(230,20, as_cmap = True)
    #One can change the vmin and vmax, but the default is sat to [-1,1]
    sea.heatmap(corr_matrix, mask = mask, cmap = cmap, vmin= -1, vmax = 1, center = 0, square = True, linewidths = 0.5, cbar_kws={'shrink': 0.5}, annot = True)
    full_save = os.path.join(save_path, title)
    plt.title(f'{title}')
    fig.savefig(f'{full_save}')
    plt.show()

#Using sys argv parser to run the code
#HOWTO: provide wished variables is as follows: 'var1, var2, var3'

parser = argparse.ArgumentParser(description='Creating correlation plots')
parser.add_argument('filepath', metavar='Filepath to datafile', help='Please enter the full path')
parser.add_argument('title_plot', metavar='Title of the Correlation Matrix', help='Enter the title - for example specify which model you are using')
parser.add_argument('savefig_path', metavar="Path to folder for saving pictures", help='Please enter the full path')
args = parser.parse_args()

filepath = args.filepath 
title_plot = args.filepath 
savefig_path = args.savefig_path

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

plot_corr(filepath, title_plot, savefig_path)

#To save figs in Malenes folder
#/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures

#Memory error for the Norkyst - will need to make the file smaller:

