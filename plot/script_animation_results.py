#animation of results
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 
import sys
import xarray as xr

def results_animation(file_path,variable,dir, frame, start_time):
    ds = xr.open_dataset(file_path) #add isel when its relevant to select which s-layer you want to look at (per now it is only the surface layer so)
    ds_var = ds[f'{variable}']
    longitude = ds["longitude"]
    latitude = ds["latitude"]
    fig,ax = plt.subplots(figsize = (12,8))
    sc = ax.scatter(longitude.values, latitude.values, c=ds_var.isel(time=start_time).values, cmap = cmocean.cm.speed)
    cbar = plt.colorbar(sc, ax=ax, orientation = "vertical", label = variable)

    def update(frame):
        sc.set_array(ds_var[frame])
        ax.set_title(f'Time step: {frame}')
        return sc 
    
    ani = FuncAnimation(fig, update, frames=range(frame), interval = 200)
    ani.save(f'{dir}/animation_{variable}.gif', writer="imagemagick")
"""
if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    raise ValueError('Please provide files as command line argument')

file_in = sys.argv[0]
file_out = sys.argv[1]
"""

def animation_compare(file_path_1, file_path_2, variable1, variable2, dir, frame, start_time):
    ds1 = xr.open_dataset(file_path_1)
    ds2 = xr.open_dataset(file_path_2)
    ds1_var = ds1[f'{variable1}']
    ds2_var = ds2[f'{variable2}'] #using variable 1 and variable 2 ensures flexibility if the datasets variable names differ slightly (ideally not though)
    longitude = ds1["longitude"]
    latitude = ds1["latitude"]
    fig,ax = plt.subplots(3, figsize = (8,10))

    if variable1 and variable2 == "temperature_0" or "Tair":
        cmap = cmocean.cm.thermal
    elif variable1 and variable2 == "salinity_0":
        cmap = cmocean.cm.haline
    elif variable1 and variable2 == "u_eastward_0" or "v_northward_0" or "Uwind" or "Vwind":
        cmap = cmocean.cm.speed
    elif variable1 and variable2 == "rain" or "cloud" or "Qair":
        cmap = cmocean.cm.rain
    elif variable1 and variable2 == "zeta":
        cmap = cmocean.cm.balance
    elif variable1 and variable2 == "Insolation":
        cmap = cmocean.cm.solar
    elif variable1 and variable2 == "Pair":
        cmap = cmocean.cm.dense

    #image1
    ds1_var_vals = ds1_var.isel(time=start_time).values
    image1 = ax[0].scatter(longitude.values, latitude.values, c=ds1_var_vals, cmap = cmap)
    cbar1 = plt.colorbar(image1, cmap=cmap, ax=ax[0], label = f'{variable1}')

    ds2_var_vals = ds2_var.isel(time=start_time).values
    image2 = ax[1].scatter(longitude.values, latitude.values, c=ds2_var_vals, cmap = cmap)
    cbar2 = plt.colorbar(image2, ax=ax[1], label = f'{variable2}')

    image3 = ax[2].scatter(longitude.values, latitude.values, c=(ds2_var_vals - ds1_var_vals))
    cbar3 = plt.colorbar(image3, cmap=cmap, ax=ax[2], label = f'{variable2} - {variable1}')
    
    