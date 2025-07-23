#animation of results
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 
import sys
import xarray as xr

#This code works fine, results are in malene/ocean-ai/plot/figures and is ran with the animation_results notebook

def results_animation(file_path,variable, dir, frame, start_time, **kwargs):
    ds = xr.open_dataset(file_path, engine="netcdf4") #add isel when its relevant to select which s-layer you want to look at (per now it is only the surface layer so)
    ds_var = ds[f'{variable}']
    longitude = ds["longitude"]
    latitude = ds["latitude"]
    fig,ax = plt.subplots(figsize = (12,8))
    sc = ax.scatter(longitude.values, latitude.values, c=ds_var.isel(time=start_time).values, cmap = cmocean.cm.speed, **kwargs)
    cbar = plt.colorbar(sc, ax=ax, orientation = "vertical", label = variable)
        
    def update(frame):
        sc.set_array(ds_var[frame])
        ax.set_title(f'Time step: {frame *3} hrs')
        ax.set_xlabel(f'Longitude [$\circ$]')
        ax.set_ylabel(f'Latitude [$\circ$]')
        return sc 
    
    ani = FuncAnimation(fig, update, frames=range(frame), interval = 400)
    ani.save(f'{dir}/animation_{variable}.gif', writer="imagemagick")

def results_absolute_val_animation(file_path,variable1, variable2, dir, frame, start_time, **kwargs):
    ds = xr.open_dataset(file_path, engine="netcdf4") #add isel when its relevant to select which s-layer you want to look at (per now it is only the surface layer so)
    ds_var_1 = ds[f'{variable1}']
    ds_var_2 = ds[f'{variable2}']
    abs_val = np.sqrt((ds_var_1 **2) + (ds_var_2**2))
    longitude = ds["longitude"]
    latitude = ds["latitude"]
    fig,ax = plt.subplots(figsize = (12,8))
    sc = ax.scatter(longitude.values, latitude.values, c=abs_val.isel(time=start_time).values, cmap = cmocean.cm.speed, **kwargs)
    cbar = plt.colorbar(sc, ax=ax, orientation = "vertical", label = '$sqrt{{variable1}²+{variable2}²}$')


    def update(frame):
        sc.set_array(abs_val[frame])
        ax.set_title(f'Time step: {frame*3} hrs')
        ax.set_xlabel(f'Longitude [$\circ$]')
        ax.set_ylabel(f'Latitude [$\circ$]')
        return sc 
    
    ani = FuncAnimation(fig, update, frames=range(frame), interval = 400)
    ani.save(f'{dir}/animation_abs_val_{variable1}_+_{variable2}.gif', writer="imagemagick")

#dir_out = f'/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures'
#results_animation(file_path='/lustre/storeB/project/fou/hi/foccus/experiments/ngpus-2017-24/inference/lam-48h-step_002016.nc', variable="v_northward_0", dir=dir_out, frame=16, start_time=0)
#results_absolute_val_animation(file_path='/lustre/storeB/project/fou/hi/foccus/experiments/ngpus-2017-24/inference/lam-48h-step_002016.nc', variable1="v_northward_0", variable2="u_eastward_0", dir = dir_out, frame=16, start_time=0)

#Legg til tingene Ina har kommentert + sjekk hvordan oppsettet blir nå, pass på at det blir en felles colorbar for image 1 og image 2 og en egen for diff!!

def animation_compare(file_path_1, file_path_2, variable1, variable2, dir, frame, start_time, title1, title2, **kwargs):
    ds1 = xr.open_dataset(file_path_1, engine = "netcdf4")
    ds2 = xr.open_dataset(file_path_2, engine = "netcdf4")#.resample(time='3H').mean(dim='time')
    ds1_var = ds1[f'{variable1}']
    ds2_var = ds2[f'{variable2}'] #using variable 1 and variable 2 ensures flexibility if the datasets variable names differ slightly (ideally not though)
    longitude = ds1["longitude"]
    latitude = ds1["latitude"]
    fig,ax = plt.subplots(3, figsize = (8,10))

    if variable1 in ["temperature_0","Tair" ] or variable2 in ["temperature_0", "Tair"]:
        cmap = cmocean.cm.thermal
    elif variable1 in ["salinity_0"] or variable2 in ["salinity_0"]:
        cmap = cmocean.cm.haline
    elif variable1 in ["u_eastward_0", "v_northward_0", "Uwind","Vwind"] or variable2 in ["u_eastward_0", "v_northward_0", "Uwind", "Vwind"]:
        cmap = cmocean.cm.speed
    elif variable1 in ["rain", "cloud", "Qair"] or variable2 in ["rain", "cloud", "Qair"]:
        cmap = cmocean.cm.rain
    elif variable1 in ["zeta"] or variable2 in ["zeta"]:
        cmap = cmocean.cm.balance
    elif variable1 in ["Insolation"] or variable2 in ["Insolation"]:
        cmap = cmocean.cm.solar
    elif variable1 in ["Pair"] or variable2 in ["Pair"]:
        cmap = cmocean.cm.dense

    #image1
    ds1_var_vals = ds1_var.isel(time=start_time).values
    image1 = ax[0].scatter(longitude.values, latitude.values, c=ds1_var_vals, cmap = cmap, **kwargs)
    cbar1 = plt.colorbar(image1, ax=ax[0], label = f'{variable1}')
    ax[0].set_title(title1)
    ax[0].set_xlabel(f'Longitude [$\circ$]')
    ax[0].set_ylabel(f'Latitude [$\circ]') 

    #image2
    ds2_var_vals = ds2_var.isel(time=start_time).values
    image2 = ax[1].scatter(longitude.values, latitude.values, c=ds2_var_vals, cmap = cmap, **kwargs)
    cbar2 = plt.colorbar(image2, ax=ax[1], label = f'{variable2}')
    ax[1].set_title(title2)
    ax[1].set_xlabel(f'Longitude [$\circ$]')
    ax[1].set_ylabel(f'Latitude [$\circ]')

    #image3
    diff = (ds2_var_vals - ds1_var_vals)
    image3 = ax[2].scatter(longitude.values, latitude.values, c=(diff), cmap = cmap, **kwargs)
    cbar3 = plt.colorbar(image3, ax=ax[2], label = f'{variable2} - {variable1}')
    ax[2].set_title(f'{variable2} - {variable1}')
    ax[2].set_xlabel(f'Longitude [$\circ$]')
    ax[2].set_ylabel(f'Latitude [$\circ]')

    image = [image1,image2, image3]
    ds = [ds1_var_vals, ds2_var_vals,diff]

    def update(frame):
        for axis, img, ds_data in zip(ax,image,ds):
            img.set_array(ds_data[frame])
            axis.set_title(f'"Time step: {frame *3} hrs')
            axis.set_xlabel(f'Longitude [$\circ$]')
            axis.set_ylabel(f'Latitude [$\circ$]')
        return image
    plt.tight_layout()
    ani = FuncAnimation(fig,update, frames=range(frame), interval = 400, blit = True)
    ani.save(f'{dir}/diff_animation_results_{variable1}_{variable2}.gif', writer="imagemagick")
    

#Running the code in PPI: 
#Finn ut av sys.argv for ulike funksjoner

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(f'Please specify the function you wish to run. Select between: "Animation", "Absolutevalue_animation", "Animation_difference')
    mode = sys.argv[1]

    if mode == "Animation":
        if len(sys.argv) < 6:
            raise ValueError(f'Please provide all necessary arguments: <file_path>, <variable>, <dir>, <frame>, <start_time>, <kwargs (optional)>')
        file_path = sys.argv[2]
        variable = sys.argv[3]
        dir = sys.argv[4]
        frame = int(sys.argv[5])
        start_time = int(sys.argv[6])

        kwargs = {}
        for arg in sys.argv[7:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        results_animation(file_path, variable, dir, frame, start_time, **kwargs)

    elif mode == "Absolutevalue_animation":
        if len(sys.argv) < 7:
            raise ValueError(f'Please provide all necessary arguments: <file_path>, <variable>, <dir>, <frame>, <start_time>, <kwargs (optional)>')
        file_path = sys.argv[2]
        variable1 = sys.argv[3]
        variable2 = sys.argv[4]
        dir = sys.argv[5]
        frame = int(sys.argv[6])
        start_time = int(sys.argv[7])

        kwargs = {}
        for arg in sys.argv[8:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        results_absolute_val_animation(file_path, variable1, variable2, dir, frame, start_time, **kwargs)

    elif mode == "Animation_difference":
        if len(sys.argv) < 8:
            raise ValueError(f'Please provide all necessary arguments: <file_path1>, <file_path2>, <variable1>, <variable2>, <dir>, <frame>, <start_time>, <title1>, <title2>, <kwargs (optional)>')
        file_path_1 = sys.argv[2]
        file_path_2 = sys.argv[3]
        variable1 = sys.argv[4]
        variable2 = sys.argv[5]
        dir = sys.argv[6]
        frame = int(sys.argv[7])
        start_time = int(sys.argv[8])

        kwargs = {}
        for arg in sys.argv[9:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        animation_compare(file_path_1, file_path_2, variable1, variable2, dir, frame, start_time, title1=f'{variable1}', title2=f'{variable2}', **kwargs)
