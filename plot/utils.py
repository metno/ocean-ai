import xarray as xr
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
import numpy as np
import cartopy
import cmocean
import cartopy.crs as ccrs
import os
import scipy.interpolate
import cartopy.feature as cfeature

#-----------------------------------------------------------------
# These functions are either a copy of or inspired by
# anemoi-utils/anemoi-utils/utils.py

def mesh(lat, lon, increment):
    """ TODO"""
    lat = np.arange(lat.min(), lat.max(), increment)
    lon = np.arange(lon.min(), lon.max(), increment)
    lat_grid, lon_grid = np.meshgrid(lat, lon)
    return lat_grid.T, lon_grid.T

def interpolate(data, lat, lon, increment):
    """ TODO"""
    era_lat_gridded, era_lon_gridded = mesh(lat, lon, increment)

    # Interpolate irregular ERA grid to regular lat/lon grid
    icoords = np.asarray([lon, lat], dtype=np.float32).T
    ocoords = np.asarray([era_lon_gridded.flatten(), era_lat_gridded.flatten()], dtype=np.float32).T

    interpolator = scipy.interpolate.NearestNDInterpolator(icoords, data) # input coordinates
    q = interpolator(ocoords)  # output coordinates
    q = q.reshape(era_lat_gridded.shape)
    return q

def panel_config_auto(ens_size, extra_panels):
    """Configure panel orientation, given
    number of ensemble members."""
    ens_size = 1 if ens_size is None else ens_size
    n_panels = ens_size
    n_panels += extra_panels

    conf_map = [None,
                (1,1), (1,2), (2,2), (2,2),
                (2,3), (2,3), (2,4), (2,4),
                (3,3), (3,4), (3,4), (3,4),
                (4,4), (4,4), (4,4), (4,4),
               ]
    panel_limit = len(conf_map) - 1

    if n_panels > panel_limit:
        print(f"Panel limit reached, continuing with {panel_limit} panels")
        n_panels = panel_limit
        ens_size = panel_limit - extra_panels

    n = conf_map[n_panels]
    return n, ens_size

def plot(ax, data, lat_grid, lon_grid, **kwargs):
    """Plot data using pcolormesh on redefined ax"""
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN, edgecolor='black')
    im = ax.pcolormesh(lon_grid, lat_grid, data, **kwargs)
    #im = ax.contourf(lon_grid, lat_grid, data)
    return im

#-----------------------------------------------------------------

def plot_landmask(ax,color='black',file='/lustre/storeB/project/fou/hi/foccus/ina/ocean-ai/plot/surface_mask_contour_paths.npy'):
    # See /lustre/storeB/project/fou/hi/foccus/ina/ocean-ai/plot/save_surface_contour.py
    contour_loaded = np.load(file, allow_pickle=True)

    # Plot each contour path
    for vertices in contour_loaded:
        ax.plot(vertices[:, 0], vertices[:, 1], color=color)

    return

def simple_mesh_plot(var_grid,lat_grid,lon_grid,time,var_name,vmin=-4,vmax=26):
    """Simple pcolormesh plot"""
    # TODO: add options for **kwargs
    kwargs = {}
    kwargs['shading'] = 'auto' ##se også på norm
    kwargs['cmap'] = 'viridis'
    kwargs['vmin'] = vmin
    kwargs['vmax'] = vmax 

    fig, ax = plt.subplots(figsize=(8, 6),squeeze=False, subplot_kw={'projection': ccrs.PlateCarree()})
    ax1=ax[0,0]
    ax1.add_feature(cfeature.BORDERS, linestyle=':') # the coastline feature is not accurate enough
    
    heatmap = ax1.pcolormesh(lon_grid, lat_grid, var_grid, **kwargs)
    # TODO: idea to use contour?
    #ax1.contourf(lon_grid, lat_grid, var_grid)
    
    # Plot the land-sea mask
    plot_landmask(ax1)

    # TODO improve this cbar and fig size etc
    cbar = fig.colorbar(heatmap, ax=ax1, orientation='vertical')
    cbar.set_label(var_name)
    ax1.set_title(f'Time step: {time}')

    ax1.set_xlim([lon_grid.min(), lon_grid.max()])
    ax1.set_ylim([lat_grid.min(), lat_grid.max()])

    return fig, ax1, heatmap

def update_anim(frame,ax,heatmap,var,time):
    """TODO"""
    heatmap.set_array(var[frame].ravel())
    ax.set_title(f'Time step: {time[frame]}')


### <----------- Functions from Malenes func_list.py --------------> 

#Calculation of speed, salinity, temp, wind and more using cartopy and cmocean colors.
#This is ideally made for zarr files 
#ToDo in use of code:
#To use the function for several timesteps, call on the function as:
#for time_indx in [time0,time1,time_n]:
    #speed(file_name, variable, year, datetime, time_indx, cbar_title)

#to run the code without getting double the figure just # out plt.show()

def plot_variable(file_name, variable, year, datetime, time_indx, cbar_title, new_file_name, cmap, **kwargs):
    file_name = file_name #the file you wish to use to plot the variables
    ds_file = open_dataset(file_name, select = variable) #open dataset and choose variable from dataset
    fig,ax = plt.subplots(figsize = (8,10), subplot_kw={"projection": ccrs.NorthPolarStereo()})
    im = ax.scatter(ds_file.longitudes, ds_file.latitudes, c = ds_file[time_indx,0,0,:], s=2, cmap = cmap, **kwargs, transform = ccrs.PlateCarree()) #time_indx is a list of time indexes when calling the function
    #ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = "black") If one wishes to add land features and thus remove values on land
    ax.coastlines()
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im, ax=ax, cax=cax, extend = "both")
    cbar.ax.set_title(cbar_title, fontsize = 14) #cbar_title: the title of the colorbar
    ax.set_title(f'+ {time_indx*3}h from {year} - {datetime}') #year of selected data + time_indx is multiplied with three because of three hour frequency in the interp forcings dataset
    path = f'/lustre/storeB/project/fou/hi/foccus/datasets/zarr_figures_verif'
    name = new_file_name
    full_path = os.path.join(path, name)
    plt.savefig(full_path)
    plt.show()
