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

########################################## f/h contours ###########################################

#Inference results
def mean_inference(ds):
    """
    Description:
    The function calculates the mean velocity for U and V ocean currents for a given period of time.  

    Inputs:
    arg[1] : ds - The dataset you wish to calculate the mean for 

    Outputs:
    The mean velocity for U and V. 
    """
    mean_u_vel = ds['u_eastward'].resample(time = 'D').mean(dim = 'time')
    mean_v_vel = ds['v_northward'].resample(time = 'D').mean(dim = 'time')
    return mean_u_vel, mean_v_vel

def fh_values_inference(ds):
    """
    Description:
    The function calculates the f/h values.

    Inputs: 
    arg[1] : ds - The dataset you wish to calculate the f/h values for. 

    Outputs:
    Returns the values for f/h. 
    """
    h = ds.h 
    f = ds.f
    f_h = f.values / h.values
    return f_h 

def fh_inference(ds, step = 5, min_l = -0.5e-5, max_l = 1.44e-5, save_path = 'figures/fh_contours.png'):

    """
    For longer time periods - use a mf dataset consisting of several inference files 
    """

    #calculate means
    u_vel, v_vel = mean_inference(ds)
    #print(f'Shape U: {u_vel.shape}. Shape V ; {v_vel.shape}.')
    #calculate f/h contours
    fh = fh_values_inference(ds)
    #plot
    fig, ax = plt.subplots(figsize = (10,12), subplot_kw={'projection' : ccrs.NorthPolarStereo()})
    step = step
    min_l = min_l
    max_l = max_l
    custom = np.linspace(min_l, max_l, 20)
    im = ax.contour(ds.lon.values[0,:,:], ds.lat[0,:,:].values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
    im_fill = ax.contourf(ds.lon[0,:,:].values, ds.lat[0,:,:].values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
    ax.quiver(ds.lon[0,:,:].values[::step, ::step], ds.lat[0,:,:].values[::step, ::step], u_vel[0,:,:].values[::step, ::step], v_vel[0,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 20)
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im_fill, ax=ax, cax = cax, extend = 'both')
    cbar.ax.set_title(r'$\frac{f}{h}$')
    gl = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
    gl.xlabels_top = False 
    gl.ylabels_right = False 
    ax.set_title(f'f/h contours and velocity field')
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')
    fig.savefig(save_path)

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
 
