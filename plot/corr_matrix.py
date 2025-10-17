import xarray as xr
import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sea
import numpy as np


#importing the dataset and selecting which variables to run the correlation matrix for the results
def import_ds(filepath):
    #Importing the dataset
    ds = xr.open_dataset(filepath)
    #Selecting variables to make the file smaller
    vars = list(ds.data_vars.keys())
    print(vars)
    return ds 

def sel_vars(filepath):
    ds = import_ds(filepath)
    user_input = input('Please provide a list of the variables you want to use seperated with commas:')
    vars_keep = [var.strip() for var in user_input.split(',')]
    vars = list(ds.data_vars.keys())
    diff = list(filter(lambda i: i not in vars_keep, vars)) #filtering out the variables from vars keep and removing them from vars
    dataset = ds.drop_vars(diff)
    print(f"All other variables removed. The variables dropped are: {diff}")
    return dataset

def plot_corr(filepath, title):
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
    fig, ax = plt.subplots(figsize=(8,10))
    cmap = sea.cubehelix_palette(230,20, as_cmap = True)
    #One can change the vmin and vmax, but the default is sat to [-1,1]
    sea.heatmap(corr_matrix, mask = mask, cmap = cmap, vmin= -1, vmax = 1, center = 0, square = True, linewidths = 0.5, cbar_kws={'shrink': 0.5}, annot = True)
    plt.title(f'{title}')
    fig.savefig(f'CorrelationMatrix_{title}')
    plt.show()

#Example on how to run the interactive version
#plot_corr('/lustre/storeB/project/fou/hi/foccus/experiments/ngpus-2017-24/inference/lam-48h-step_002016.nc', 'Ngpus_vars_speed')
#provide wished variables as following: 'var1, var2, var3'
