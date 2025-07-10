#animation of windfields
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 


def anim_wind(file_name, variable):
    ds = open_dataset(file_name, select = variable)
    fig,ax = plt.subplots(figsize=(12,8))
    sc = ax.scatter(ds.longitudes, ds.latitudes, c=ds[0,0,0,:], s = 2, cmap = cmocean.cm.speed)
    return sc, ds, fig, ax

def anim_wind_abs(file_name, variable1, variable2):
    ds = open_dataset(file_name, select = [variable1,variable2])
    abs = np.sqrt(ds[0,0,0,:]**2 + ds[0,1,0,:]**2)
    fig,ax = plt.subplots(figsize=(12,8))
    sc = ax.scatter(ds.longitudes, ds.latitudes, c=abs, s = 2, cmap = cmocean.cm.speed)
    return sc, ds, fig, ax

def update_abs(frame, file_name, variable1, variable2):
    anim_wind_abs(file_name=file_name, variable=variable1, variable2= variable2)   
    sc.set_array(ds[frame,0,0,:])
    ax.set_title(f'Time step: {frame}')
    ani = FuncAnimation(fig, update_abs, frames = range(frame), interval = 200)
    ani.save(f"temp_animation_0_25_2023_{variable1}_{variable2}.gif", writer = "imagemagick")
    return ani.save

def update(frame, file_name, variable):
    anim_wind(file_name=file_name, variable=variable)   
    sc.set_array(ds[frame,0,0,:])
    ax.set_title(f'Time step: {frame}')
    ani = FuncAnimation(fig, update, frames = range(frame), interval = 200)
    ani.save(f"temp_animation_0_25_2023_{variable}.gif", writer = "imagemagick")
    return ani.save


anim_wind(file_name='/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_2023.zarr', variable={"Vwind_northward"})
anim_wind_abs(file_name='/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_2023.zarr', variable1 = "Uwind_eastward", variable2 = "Vwind_northward")

#have ran the file but nothing is saved?? 