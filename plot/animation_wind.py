#animation of windfields
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 

#Function for one variable    
def anim_wind(file_name, variable, frame):
    ds = open_dataset(file_name, select = variable)
    fig,ax = plt.subplots(figsize=(12,8))
    sc = ax.scatter(ds.longitudes, ds.latitudes, c=ds[0,0,0,:], s = 2, cmap = cmocean.cm.speed)
    cbar = plt.colorbar(sc, ax=ax, orientation = "vertical", label = variable)
    
    def update(frame): 
        sc.set_array(ds[frame,0,0,:])
        ax.set_title(f'Time step: {frame}')
        return sc
    
    ani = FuncAnimation(fig, update, frames = range(frame), interval = 200)
    ani.save(f"wind_animation_2023_{variable}.gif", writer = "imagemagick")

    
#Function to calculate the absolute value of two variables
def anim_wind_abs(file_name, variable1, variable2, frame):
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
    ani.save(f"wind_animation_2023_{variable1}_{variable2}.gif", writer = "imagemagick")

#Examples on how to call on functions:

#anim_wind(file_name='/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_2023.zarr', variable={"Vwind_northward"}, frame=48)
#anim_wind_abs(file_name='/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_2023.zarr', variable1 = "Uwind_eastward", variable2 = "Vwind_northward", frame=48)
