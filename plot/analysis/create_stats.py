#Import necessary packages
import xarray as xr
import matplotlib.pyplot as plt 
import pandas as pd
import seaborn as sea
import numpy as np
import sys 
import argparse
import os 
import cartopy 
import cmocean 
import cartopy.crs as ccrs 
import cartopy.feature as cfeature
from sklearn.metrics import root_mean_squared_error
from sklearn.linear_model import LinearRegression
from matplotlib.lines import Line2D


##########################################Correlation Matrix###########################################

def correlation_matrix(ds, save_path = 'figures/corr_matrix.png'):
    """
    Description:
    This function takes in a dataset and returns a correlation matrix for selected variables from the datafile. 

    Args:
    args[1] : Inference dataset. 
    args[2] : Path to store the figure + figure name. 
    """

    vars_keep = ['salinity', 'temperature', 'u_eastward', 'v_northward']
    vars = list(ds.data_vars.keys())
    diff = list(filter(lambda i: i not in vars_keep, vars)) 
    dataset = ds.drop_vars(diff)
    dataset_pd = dataset.to_dataframe()

    corr_matrix = dataset_pd.corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    fig, ax = plt.subplots(figsize=(12,10))
    cmap = sea.cubehelix_palette(230,20, as_cmap = True)
    sea.heatmap(corr_matrix, mask = mask, cmap = cmap, vmin= -1, vmax = 1, center = 0, square = True, linewidths = 0.5, cbar_kws={'shrink': 0.5}, annot = True)
    plt.title(f'Correlation Matrix')
    fig.savefig(f'{save_path}')

########################################## RMSE (NRMSE) ###########################################

def rmse(truth, predicted, inf = 0, save_path = 'figures/rmse.png', suptitle = 'RMSE per variable', min_max_scaled = True):

    """
    Description: 
    Function for calculating RMSE. The function will scale the data as a min-max scaling as long as min-max-scaled = True. 

    Arguments: 
    arg[1] : Truth (dataset) - The Norkyst3 dataset which is always given as the truth in this case
    arg[2] : Predicted (dataset) - The HavBris dataset which is always the predicted one in this case
    arg[3] : Inf (int) - selecting which inference file to plot 

    Output: 
    An RMSE-figure for each predicted variable in Havbris
    """

    #Resample truth datastep 3hrs
    truth_resampled = truth.resample(time = '3H').mean()
    """Dont neccesary to rename anymore I believe, when using open_dataset function"""
    #truth_rename = truth_resampled.rename({'X' : 'Y', 'Y' : 'X'})

    predicted_choose_inf = predicted.isel(inf_file = inf)

    #Remove first time step of datasets and align shapes 
    truth_skip_timestep = truth_resampled.isel(time = slice(1,None))
    predicted_skip_timestep = predicted_choose_inf.isel(time=slice(1,None))
    
    #Variables to select
    target_vars = ['u_eastward', 'v_northward', 'temperature', 'salinity']

    normalized_by_timestep = {}
    rmse_total = {}

    for var in target_vars:
        nk_data = truth_skip_timestep[var]
        hb_data = predicted_skip_timestep[var]

        #calculating MSE and RMSE using groupby for each timestep
        error = (nk_data - hb_data)
        mse_by_timestep = (error **2).groupby('time').mean(['Y', 'X'])
        rmse_by_timestep = np.sqrt(mse_by_timestep)

        if min_max_scaled:
            normalized_by_timestep[var] = rmse_by_timestep / (hb_data.max() - hb_data.min())
        else: 
            normalized_by_timestep[var] = rmse_by_timestep

        #Total RMSE (remove NANs)
        mask = ~np.isnan(nk_data) & ~np.isnan(hb_data)
        rmse_total_before_n = root_mean_squared_error(nk_data.values[mask], hb_data.values[mask])
        if min_max_scaled:
            rmse_total[var] = rmse_total_before_n / (hb_data.max() - hb_data.min())
        else: 
            rmse_total[var] = rmse_total_before_n

    #plotting
    fig, ax = plt.subplots(2,2, figsize = (12,14))
    labels = ['U-eastward', 'V-northward', 'Temperature', 'Salinity']
    for i, var in enumerate(target_vars):
        row, col = divmod(i,2)
        ax[row, col].set_title(labels[i])
        ax[row, col].scatter(normalized_by_timestep[var].time, normalized_by_timestep[var], label = 'NRMSE per timestep', color = 'darkolivegreen', linestyle = ':')
        ax[row, col].plot(normalized_by_timestep[var].time, normalized_by_timestep[var], label = 'NRMSE per timestep', color = 'darkkhaki', linestyle = '-')
        ax[row, col].axhline(rmse_total[var], color = 'm', linestyle = '--', label = f'Total RMSE: {rmse_total[var]:.5f}')
        plt.setp(ax[row,col].xaxis.get_majorticklabels(), rotation =45)
        ax[row, col].legend()
        ax[row,col].grid(True)
    plt.suptitle(f'{suptitle}')
    fig.savefig(save_path)


########################################## Histograms ###########################################

def histograms(ds, time_to_check = 1, save_path = 'figures/histogram.png'):
    """
    Definition: 

    Arguments:
    arg[1] : dataset - the inference dataset 
    arg[2] : time to check (int) - the timestep in the data would you like the check the variable distribution for

    Outputs: 
    Figure of the variable distributions 
    """

    variables = ['temperature', 'salinity', 'u_eastward', 'v_northward']
    data = {var : ds[var].isel(time = time_to_check).values.ravel() for var in variables}
    data = {var : values[~np.isnan(values)] for var, values in data.items()}

    sea.set_theme(style="darkgrid")

    fig, ax = plt.subplots(2,2, figsize = (12,12))
    titles = ['Temperature', 'Salinity', 'U-Eastward', 'V-Northward']

    for i, (var, values) in enumerate(data.items()):
        row, col = divmod(i,2)
        sea.histplot(values, bins = 30, kde = True, ax = ax[row, col], stat='density', color = 'royalblue', edgecolor = 'darkolivegreen')
        ax[row, col].set_title(titles[i], fontsize = 15)
        #ax[row, col].

    plt.suptitle(f'Histogram & Density curve for Havbris variables')
    plt.tight_layout()
    fig.savefig(save_path)
 
