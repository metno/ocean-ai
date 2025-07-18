#animation of results
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 
import sys
import xarray as xr

#I think the code is ok? And that the white areas might be lack of values in the result files???

def results_animation(file_path,variable, dir, frame, start_time):
    ds = xr.open_dataset(file_path, engine="netcdf4") #add isel when its relevant to select which s-layer you want to look at (per now it is only the surface layer so)
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

def results_absolute_val_animation(file_path,variable1, variable2, dir, frame, start_time):
    ds = xr.open_dataset(file_path, engine="netcdf4") #add isel when its relevant to select which s-layer you want to look at (per now it is only the surface layer so)
    ds_var_1 = ds[f'{variable1}']
    ds_var_2 = ds[f'{variable2}']
    abs_val = np.sqrt((ds_var_1 **2) + (ds_var_2**2))
    longitude = ds["longitude"]
    latitude = ds["latitude"]
    fig,ax = plt.subplots(figsize = (12,8))
    sc = ax.scatter(longitude.values, latitude.values, c=abs_val.isel(time=start_time).values, cmap = cmocean.cm.speed)
    cbar = plt.colorbar(sc, ax=ax, orientation = "vertical", label = f'absolute value of{variable1} and {variable2}')

    def update(frame):
        sc.set_array(abs_val[frame])
        ax.set_title(f'Time step: {frame}')
        return sc 
    
    ani = FuncAnimation(fig, update, frames=range(frame), interval = 200)
    ani.save(f'{dir}/animation_abs_val_{variable1}_+_{variable2}.gif', writer="imagemagick")
"""
if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    raise ValueError('Please provide files as command line argument')

file_in = sys.argv[0]
dir_out = sys.argv[1]
#start_time_in = sys.argv[2]
"""
dir_out = f'/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures'
results_animation(file_path='/lustre/storeB/project/fou/hi/foccus/experiments/ngpus-2017-24/inference/lam-48h-step_002016.nc', variable="v_northward_0", dir=dir_out, frame=16, start_time=0)
results_absolute_val_animation(file_path='/lustre/storeB/project/fou/hi/foccus/experiments/ngpus-2017-24/inference/lam-48h-step_002016.nc', variable1="v_northward_0", variable2="u_eastward_0", dir = dir_out, frame=16, start_time=0)

"""
def animation_compare(file_path_1, file_path_2, variable1, variable2, dir, frame, start_time, title1, title2):
    ds1 = xr.open_dataset(file_path_1, enginge = "netcdf4")
    ds2 = xr.open_dataset(file_path_2, engine = "netcdf4")
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
    ax[0].set_title(title1)
    ax[0].set_xlabel(f'Longitude [$\circ$]')
    ax[0].set_ylabel(f'Latitude [$\circ]')

    #image2
    ds2_var_vals = ds2_var.isel(time=start_time).values
    image2 = ax[1].scatter(longitude.values, latitude.values, c=ds2_var_vals, cmap = cmap)
    cbar2 = plt.colorbar(image2, ax=ax[1], label = f'{variable2}')
    ax[1].set_title(title2)
    ax[1].set_xlabel(f'Longitude [$\circ$]')
    ax[1].set_ylabel(f'Latitude [$\circ]')

    #image3
    image3 = ax[2].scatter(longitude.values, latitude.values, c=(ds2_var_vals - ds1_var_vals))
    cbar3 = plt.colorbar(image3, cmap=cmap, ax=ax[2], label = f'{variable2} - {variable1}')
    ax[2].set_title(f'{variable2} - {variable1}')
    ax[2].set_xlabel(f'Longitude [$\circ$]')
    ax[2].set_ylabel(f'Latitude [$\circ]')
    
    plt.tight_layout()

    def update(frame):
        image1.set_array(ds1_var_vals[frame])
        ax.set_title(f'"Time step: {frame}')

        #finn en måte å iterere gjennom image 1,2,3! 
        
    
"""    