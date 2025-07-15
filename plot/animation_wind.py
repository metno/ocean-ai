#animation of windfields
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 
import sys

#Function for one variable    
def anim_wind(file_name, dir, variable, frame):
    ds = open_dataset(file_name, select = variable)
    fig,ax = plt.subplots(figsize=(12,8))
    sc = ax.scatter(ds.longitudes, ds.latitudes, c=ds[0,0,0,:], s = 2, cmap = cmocean.cm.speed)
    cbar = plt.colorbar(sc, ax=ax, orientation = "vertical", label = variable)
    
    def update(frame): 
        sc.set_array(ds[frame,0,0,:])
        ax.set_title(f'Time step: {frame}')
        return sc
    
    ani = FuncAnimation(fig, update, frames = range(frame), interval = 200)
    ani.save(f"{dir}/wind_animation_2023_{variable}.gif", writer = "imagemagick")

    
#Function to calculate the absolute value of two variables
def anim_wind_abs(file_name,dir, variable1, variable2, frame):
    ds = open_dataset(file_name, select = [variable1,variable2])
    abs = np.sqrt(ds[0,0,0,:]**2 + ds[0,1,0,:]**2)
    fig,ax = plt.subplots(figsize=(12,8))
    sc = ax.scatter(ds.longitudes, ds.latitudes, c=abs, s = 2, cmap = cmocean.cm.speed)
    cbar = plt.colorbar(sc, ax = ax, orientation = "vertical", label = f'Abs val of {variable1} and {variable2}')

    def update_abs(frame):
        abs = np.sqrt(ds[frame,0,0,:]**2 + ds[frame,1,0,:]**2)   
        sc.set_array(abs)
        ax.set_title(f'Time step: {frame}')
        return sc
    
    ani = FuncAnimation(fig, update_abs, frames = range(frame), interval = 200)
    ani.save(f"{dir}/wind_animation_2023_{variable1}_{variable2}.gif", writer = "imagemagick")


if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    raise ValueError('Please provide files as command line argument')

file_in = sys.argv[1]
dir_out = sys.argv[2]

#Examples on how to call on functions:

# python animation_wind.py file_in dir_out
# dir_in= '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_2023.zarr'
# dir_save = '/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures/'

#anim_wind(file_name=file_in, dir=dir_out, variable="u_eastward_0", frame=48)
#anim_wind(file_name=file_in, dir=dir_out, variable="v_northward_0", frame=48)
anim_wind_abs(file_name=file_in, dir=dir_out, variable1 = "u_eastward_0", variable2 = "v_northward_0", frame=48)