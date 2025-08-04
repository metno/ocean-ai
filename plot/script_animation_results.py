#animation of results
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 
import sys
import xarray as xr

#These scripts are adapted to the nc result files, though file_path2 and 3 in the last function is meant for two dimensional norkyst models.
#One has to adapt this code to match it to two-dimensional data or rewrite the script to select based on the datatype. The last mentioned is a possible reason
#Animation of a single variable
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

#Animation of absolute values from a dataset
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

#Animation compare does currently not work due to the differences between the datsets, giving troubles in plotting
def animation_compare(file_path_1, file_path_2, file_path_3, variable1, variable2, dir, frame, start_time, title1, title2, **kwargs):
    ds1 = xr.open_dataset(file_path_1, engine = "netcdf4").isel(time=slice(0,16))
    ds2 = xr.open_mfdataset([file_path_2,file_path_3]).isel(s_rho=-1)
    ds1_var = ds1[f'{variable1}']
    ds1_var = np.array(ds1_var)
    #ds1_var = np.pad(ds1_var, ((0,0), (0,77500)), mode = "edge")
    ds2_var = ds2[f'{variable2}'].resample(time='3H').mean(dim='time')
    ds2_var = np.array(ds2_var)
    ds2_var = ds2_var.reshape(ds2_var.shape[-3],-3)
    ds1_var = ds1_var.reindex_like(ds2_var, method = 'nearest')
    longitude = ds1["longitude"] 
    latitude = ds1["latitude"]
    lon = ds2["lon"]
    lat = ds2["lat"]
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
    print(f'Image 1 - before')
    print(f'lon: {longitude.shape}, lat: {latitude.shape}, ds1_var_vals: {ds1_var.shape}')
    image1 = ax[0].scatter(lon, lat, c=ds1_var[start_time], cmap = cmap, **kwargs)
    cbar1 = plt.colorbar(image1, ax=ax[0], label = f'{variable1}')
    ax[0].set_title(title1)
    ax[0].set_xlabel(f'Longitude [$\circ$]')
    ax[0].set_ylabel(f'Latitude [$\circ$]') 
    print(f'Image 1 - after')

    #image2 
    print(f'ds_var_vals:{ds2_var.shape}, lon: {lon.shape}, lat: {lat.shape}')
    image2 = ax[1].scatter(lon, lat, c=ds2_var[start_time], cmap = cmap, **kwargs)
    cbar2 = plt.colorbar(image2, ax=ax[1], label = f'{variable2}')
    ax[1].set_title(title2)
    ax[1].set_xlabel(f'Longitude [$\circ$]')
    ax[1].set_ylabel(f'Latitude [$\circ]$')
    print(f'Image 2 - after')

    #image3
    diff = (ds2_var - ds1_var)
    print(f'Image 3 - before')
    image3 = ax[2].scatter(lon, lat, c=(diff), cmap = cmap, **kwargs)
    cbar3 = plt.colorbar(image3, ax=ax[2], label = f'{variable2} - {variable1}')
    ax[2].set_title(f'{variable2} - {variable1}')
    ax[2].set_xlabel(f'Longitude [$\circ$]')
    ax[2].set_ylabel(f'Latitude [$\circ$]')
    print(f'Image 3 - after')

    image = [image1,image2, image3]
    ds = [ds1_var, ds2_var,diff]

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
    


#compare two animations of different datasets in same subplot, without the difference:
#the norkyst dataset should be selected as file_path 2 and 3 because ngpus is of longer timescales.
def compare_two(file_path_1, file_path_2, file_path_3, variable1, variable2, dir, frame, start_time, title1, title2, **kwargs):
    ds1 = xr.open_dataset(file_path_1, engine = "netcdf4").isel(time=slice(0,16)) #0,16 time steps to match 48 hrs timestep in Norkyst files when merging two datasets
    ds2 = xr.open_mfdataset([file_path_2,file_path_3]).isel(s_rho=-1) #import two Norkyst datasets to match the time indx
    ds1_var = ds1[f'{variable1}']
    ds2_var = ds2[f'{variable2}'].resample(time='3H').mean(dim='time') #Resampling the Norkyst file to match the resultfiles frequency of three hrs
    ds2_var = np.array(ds2_var)
    ds2_var = ds2_var.reshape(ds2_var.shape[-3], -3) #rehaping the Norkyst model to merge X and Y dims
    longitude = ds1["longitude"] 
    latitude = ds1["latitude"]
    lon = ds2["lon"].values
    lat = ds2["lat"].values
    fig,ax = plt.subplots(2, figsize = (8,14))

    #If tests - changing the colors of the animation depending on which variable is being plotted. 
    #Based on the cmocean colorbars for different oceanographic phenomena 
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
    print(f'Image 1 - before')
    print(f'lon: {longitude.shape}, lat: {latitude.shape}, ds1_var_vals: {ds1_var.shape}')
    image1 = ax[0].scatter(longitude.values, latitude.values, c=ds1_var[start_time].values, cmap = cmap, **kwargs)
    cbar1 = plt.colorbar(image1, ax=ax[0], label = f'Result ngpus: {variable1}')
    ax[0].set_title(title1)
    ax[0].set_xlabel(f'Longitude [$\circ$]')
    ax[0].set_ylabel(f'Latitude [$\circ$]') 
    print(f'Image 1 - after')
    
    #image2 
    print(f'ds_var_vals:{ds2_var.shape}, lon: {lon.shape}, lat: {lat.shape}')
    image2 = ax[1].scatter(lon, lat, c=ds2_var[start_time], cmap = cmap, **kwargs)
    cbar2 = plt.colorbar(image2, ax=ax[1], label = f'Norkyst 800: {variable2}')
    ax[1].set_title(title2)
    ax[1].set_xlabel(f'Longitude [$\circ$]')
    ax[1].set_ylabel(f'Latitude [$\circ]$')
    print(f'Image 2 - after')

    image = [image1,image2]
    ds = [ds1_var, ds2_var]

    #Creating the animations
    def update(frame):
        for axis, img, ds_data in zip(ax,image,ds):
            img.set_array(ds_data[frame])
            axis.set_title(f'Time step: + {frame *3} hrs from 2024-04-02')
            axis.set_xlabel(f'Longitude [$\circ$]')
            axis.set_ylabel(f'Latitude [$\circ$]')
        return image
    plt.tight_layout()
    ani = FuncAnimation(fig,update, frames=range(frame), interval = 400, blit = True)
    ani.save(f'{dir}/compare_animation_results_{variable1}_{variable2}.gif', writer="imagemagick")
    
    

#Running the code in PPI: 
#Important to mention the mode you want to plot (Animation_difference currently not in use)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(f'Please specify the function you wish to run. Select between: "Animation", "Absolutevalue_animation", "Animation_difference', 'Compare')
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
        file_path_3 = sys.argv[4]
        variable1 = sys.argv[5]
        variable2 = sys.argv[6]
        dir = sys.argv[7]
        frame = int(sys.argv[8])
        start_time = int(sys.argv[9])

        kwargs = {}
        for arg in sys.argv[10:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        animation_compare(file_path_1, file_path_2, file_path_3, variable1, variable2, dir, frame, start_time, title1=f'{variable1}', title2=f'{variable2}', **kwargs)

    elif mode == "Compare":
        print("running compare module")
        if len(sys.argv) < 9:
            raise ValueError(f'Please provide all necessary arguments: <file_path1>, <file_path2>, <variable1>, <variable2>, <dir>, <frame>, <start_time>, <title1>, <title2>, <kwargs (optional)>')
        for i in range (9):
            print(sys.argv[i])
        file_path_1 = sys.argv[2]
        file_path_2 = sys.argv[3]
        file_path_3 = sys.argv[4]
        variable1 = sys.argv[5]
        variable2 = sys.argv[6]
        dir = sys.argv[7]
        frame = int(sys.argv[8])
        start_time = int(sys.argv[9])

        kwargs = {}
        for arg in sys.argv[10:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        compare_two(file_path_1, file_path_2, file_path_3, variable1, variable2, dir, frame, start_time, title1=f'Ngpus {variable1}', title2=f'Norkyst800 {variable2}', **kwargs)
