import xarray as xr
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
import numpy as np
import cartopy
import cmocean
import cartopy.crs as ccrs

#Calculation of speed, salinity, temp, wind and more using cartopy and cmocean colors.
#This is ideally made for zarr files 
#ToDo in use of code:
#To use the function for several timesteps, call on the function as:
#for time_indx in [time0,time1,time_n]:
    #speed(file_name, variable, year, time_indx, cbar_title)

def speed(file_name, variable, year, datetime, time_indx, cbar_title):
    file_name = file_name #the file you wish to use to plot the variables
    ds_file = open_dataset(file_name, select = variable) #open dataset and choose variable from dataset
    fig,ax = plt.subplots(figsize = (8,10), subplot_kw={"projection": ccrs.NorthPolarStereo()})
    im = ax.scatter(ds_file.longitudes, ds_file.latitudes, c = ds_file[time_indx,0,0,:], s=2, cmap = cmocean.cm.speed, transform = ccrs.PlateCarree()) #time_indx is a list of time indexes when calling the function
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = "black")
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im, ax=ax, cax=cax, extend = "both")
    cbar.ax.set_title(cbar_title, fontsize = 14) #cbar_title: the title of the colorbar
    ax.set_title(f'+ {time_indx}h from {year} - {datetime}') #year of selected data + time
    plt.show()

def salinity(file_name, variable, year, datetime, time_indx, cbar_title):
    file_name = file_name #the file you wish to use to plot the variables
    ds_file = open_dataset(file_name, select = variable) #open dataset and choose variable from dataset
    fig,ax = plt.subplots(figsize = (8,10), subplot_kw={"projection": ccrs.NorthPolarStereo()})
    im = ax.scatter(ds_file.longitudes, ds_file.latitudes, c = ds_file[time_indx,0,0,:], s=2, vmin = 30, cmap = cmocean.cm.haline, transform = ccrs.PlateCarree()) #vmin can be changed and vmax can be added
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = "black")
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im, ax=ax, cax=cax, extend = "both")
    cbar.ax.set_title(cbar_title, fontsize = 14)
    ax.set_title(f'+ {time_indx}h from {year} - {datetime}')
    plt.show()

def temp(file_name, variable, year, datetime, time_indx, cbar_title):
    file_name = file_name #the file you wish to use to plot the variables
    ds_file = open_dataset(file_name, select = variable) #open dataset and choose variable from dataset
    fig,ax = plt.subplots(figsize = (8,10), subplot_kw={"projection": ccrs.NorthPolarStereo()})
    im = ax.scatter(ds_file.longitudes, ds_file.latitudes, c = ds_file[time_indx,0,0,:], s=2, vmin = 30, cmap = cmocean.cm.thermal, transform = ccrs.PlateCarree())
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = "black")
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im, ax=ax, cax=cax, extend = "both")
    cbar.ax.set_title(cbar_title, fontsize = 14)
    ax.set_title(f'+ {time_indx}h from {year} - {datetime}')
    plt.show()

