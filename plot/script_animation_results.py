#animation of results
from anemoi.datasets import open_dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cmocean  
import numpy as np 
import sys
import xarray as xr
import cartopy.crs as ccrs
import cartopy


"""
NEW CODE FOR 2D RESULTS
"""

def results_animation(file_path, variable, dir, model_name, frame = 16, start = 0,  **kwargs):
    """
    Description: 
    Function returning an animation for 2D results for the inference results. 
    This returns a single animation for a given variable. 

    Arguments:
    arg[1] : Filepath (str) - Filepath for the dataset you wish to produce animations for.
    arg[2] : Variable (str) - The variable you wish to plot. 
    arg[3] : Dir (str) - Filepath for the location to save the animation in. 
    arg[4] : Start (optional, float) - the start time for the animation. Default is 0. 
    arg[5] : Frame (optional, float) - The number of frames / timesteps. Default is 16 for inference dataset (48hrs). 
    arg[6] : Model (str) - Model name - included in name save
    arg[6] : **args (optional) - Include arguments such as vmin and vmax etc. if wanted. 

    Returns: 
    An animation saved in the dir folder.
    """
    ds = xr.open_dataset(file_path, engine="netcdf4") #add .isel(s_rho = -1) when expanding to 3D model
    ds_var = ds[f'{variable}']
    print(f'Dataset imported and variable: {variable} is chosen')
    fig,ax = plt.subplots(figsize = (12,8))
    sc = ax.pcolormesh(ds_var[start], cmap = cmocean.cm.speed, **kwargs)
    cbar = fig.colorbar(sc, ax=ax, orientation = "vertical", label = variable, extend = 'both')
        
    def update(frame):
        sc.set_array(ds_var[frame])
        ax.set_title(f'Time step: {frame *3} hrs, model = {model_name}')
        ax.set_xlabel(f'Y')
        ax.set_ylabel(f'X')
        return sc 
    ani = FuncAnimation(fig, update, frames=range(frame), interval = 400)
    print('Trying to save it')
    ani.save(f'{dir}/animation_{variable}_{model_name}.gif', writer="imagemagick")



#Animation of absolute values from a dataset
def absolute_val(file_path, variable1, variable2, dir, model_name, frame = 16, start = 0, **kwargs):
    """
    Description: 
    Function returning an animation for 2D results for the inference results. 
    This returns a single animation for the absolute value of two variables. Ideal in use for ocean currents for example (u_eastward_0 and v_northward_0).

    Arguments: 
    arg[1] : Filepath (str) - Filepath for the dataset you wish to produce animations for.
    arg[2] : Variable 1 (str) - Variable 1 to plot
    arg[3] : Variable 2 (str) - Variable 2 to plot
    arg[4] : Dir (str) - Filepath for the location to save the figure in
    arg[5] : Model name (str) - included in save name and title
    arg[6] : Frame (optional, float) - The number of frames / timesteps. Default is 16 for inference dataset (48hrs).
    arg[7] : Start (optional, float) - the start time for the animation. Default is 0.
    arg[8] : **args (optional) - Include arguments such as vmin and vmax etc. if wanted.

    Returns: 
    An animation saved in the dir folder.
    """
    ds = xr.open_dataset(file_path, engine="netcdf4")  #add .isel(s_rho = -1) when expanding to 3D model
    ds_var_1 = ds[f'{variable1}']
    ds_var_2 = ds[f'{variable2}']
    print(f'The following variables are selected: {variable1} and {variable2}')
    abs_val = np.sqrt((ds_var_1 **2) + (ds_var_2**2))
    fig,ax = plt.subplots(figsize = (12,8))
    sc = ax.pcolormesh(abs_val[start], cmap = cmocean.cm.speed, **kwargs)
    cbar = fig.colorbar(sc, ax=ax, orientation = "vertical", label = '$\sqrt{U²+V²}$', extend = 'both')


    def update(frame):
        sc.set_array(abs_val[frame])
        ax.set_title(f'Time step: {frame*3} hrs for model {model_name}')
        ax.set_xlabel(f'Y')
        ax.set_ylabel(f'X')
        return sc 
    
    ani = FuncAnimation(fig, update, frames=range(frame), interval = 400)
    ani.save(f'{dir}/animation_abs_val_{variable1}_+_{variable2}_{model_name}.gif', writer="imagemagick")


def animation_compare(file_path_1, file_path_2, file_path_3, variable1, variable2, dir, model_name,  title1 = 'Havbris', title2 = 'Norkyst', frame = 16, start_time = 0, **kwargs):

    print(f'Sys argv: {sys.argv}')

    """"
    Description: 
    Function returning an animation for 2D results for Havbris, the Norkyst Hindcast and calculates the difference between the models. 
    This returns a single animation for the absolute value of two variables. Ideal in use for ocean currents for example (u_eastward_0 and v_northward_0).

    Arguments: 
    arg[1] : Filepath1 (str) - Filepath for the Havbris dataset you wish to produce animations for (48hrs)
    arg[2] : Filepath2 (str) - Filepath for the Norkyst dataset you wish to produce animations for (24hrs)
    arg[3] : Filepath3 (str) - Filepath for the Norkyst dataset you wish to produce animations for (24hrs)
    arg[4] : Variable 1 (str) - Variable 1 to plot (For Havbris, examples: salinity_0 and u_northward_0)
    arg[5] : Variable 2 (str) - Variable 2 to plot (For Norkyst, examples: salinity and u_northward)
    arg[6] : Dir (str) - Filepath for the location to save the figure in
    arg[7] : Model name (str) - included in save name
    arg[8] : Title1 (str) - Title of the first animation. Default = Havbris. 
    arg[9] : Title2 (str) - Title of the second animation. Default = Norkyst. 
    arg[10] : Frame (optional, float) - The number of frames / timesteps. Default is 16 for inference dataset (48hrs).
    arg[11] : Start (optional, float) - the start time for the animation. Default is 0.
    arg[12] : **args (optional) - Include arguments such as vmin and vmax etc. if wanted.

    Returns: 
    An animation saved in the dir folder. 
    """
    ds_hbris = xr.open_dataset(file_path_1, engine='netcdf4').isel(time = slice(0,16))
    ds_nor = xr.open_mfdataset([file_path_2, file_path_3]).isel(s_rho = -1)
    ds_hbris_var = ds_hbris[f'{variable1}']
    ds_nor_var = ds_nor[f'{variable2}'].resample(time = '3H').mean(dim = 'time')
    print(f'The following variables are selected: {variable1} and {variable2}')

    fig,ax = plt.subplots(3, figsize = (8,14))

    if variable1 in ["temperature_0","Tair"] or variable2 in ["temperature_0", "Tair"]:
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

    #Image1 - Havbris
    image1 = ax[0].pcolormesh(ds_hbris_var[start_time], cmap = cmap, shading = 'nearest', **kwargs)
    cbar1 = plt.colorbar(image1, ax=ax[0], label = f'{variable1}')
    ax[0].set_title(title1)
    ax[0].set_xlabel(f'Y')
    ax[0].set_ylabel(f'X')

    #Image2 - Norkyst
    image2 = ax[1].pcolormesh(ds_nor_var[start_time], cmap = cmap,  shading = 'nearest', **kwargs)
    cbar2 = plt.colorbar(image2, ax=ax[1], label = f'{variable2}') 
    ax[1].set_title(title2)
    ax[1].set_xlabel(f'Y')
    ax[1].set_ylabel(f'X')

 #Image3 - Diff
    diff = (ds_nor_var - ds_hbris_var)
    image3 = ax[2].pcolormesh(diff[start_time], cmap = cmap, shading = 'nearest', **kwargs)
    cbar3 = plt.colorbar(image3, ax=ax[2], label = f'{variable2} - {variable1}')
    ax[2].set_title(f'Difference')
    ax[2].set_xlabel(f'Y')
    ax[2].set_ylabel(f'X')

    image = [image1, image2, image3]
    ds = [ds_hbris_var, ds_nor_var, diff]
    
    def update(frame):
        updated = []
        for i, (axis, img, ds_data) in enumerate(zip(ax,image,ds)):
            img.set_array(ds_data[frame])
            if i == 0:
                axis.set_title(f'{title1} - Time step: {frame *3} hrs')
            elif i == 1:
                axis.set_title(f'{title2} - Time step: {frame * 3} hrs')
            elif i == 2:
                axis.set_title(f'Difference - Time step: {frame *3} hrs')
            axis.set_xlabel(f'Y')
            axis.set_ylabel(f'X')
            updated.append(img)
        return updated
    
    plt.tight_layout()
    ani = FuncAnimation(fig,update, frames=range(frame), interval = 400, blit = True)
    ani.save(f'{dir}/diff_animation_results_{variable1}_{variable2}_{model_name}.gif', writer="imagemagick")


#Running the code in PPI: 
#Important to mention the mode you want to plot!
#Run script in ppi-sub-animation

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(f'Please specify the function you wish to run. Select between: "Animation", "Absolutevalue_animation", "Animation_difference')
    mode = sys.argv[1]

    if mode == "Animation":
        if len(sys.argv) < 7:
            raise ValueError(f'Please provide all necessary arguments: <file_path>, <variable>, <dir>, <model_name>, <frame (default = 16)>, <start (default = 0)>, <kwargs (optional)>')
        file_path = sys.argv[2]
        variable = sys.argv[3]
        dir = sys.argv[4]
        model_name = sys.argv[5]
        frame = int(sys.argv[6])
        start = int(sys.argv[7])

        kwargs = {}
        for arg in sys.argv[8:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        results_animation(file_path, variable, dir, model_name, frame, start, **kwargs)

    elif mode == "Absolutevalue_animation":
        if len(sys.argv) < 8:
            raise ValueError(f'Please provide all necessary arguments: <file_path>, <variable1>, <variable2>, <dir>, <model_name>, <frame (default = 16)>, <start (default = 0)>, <kwargs (optional)>')
        file_path = sys.argv[2]
        variable1 = sys.argv[3]
        variable2 = sys.argv[4]
        dir = sys.argv[5]
        model_name = sys.argv[6]
        frame = int(sys.argv[7])
        start = int(sys.argv[8])

        kwargs = {}
        for arg in sys.argv[9:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        absolute_val(file_path, variable1, variable2, dir, model_name, frame, start, **kwargs)

    elif mode == "Animation_difference":
        print(f'Running the animation difference')
        if len(sys.argv) < 12:
            raise ValueError(f'Please provide all necessary arguments: <file_path1>, <file_path2>, <file_path3> , <variable1>, <variable2>, <dir>, <model_name>, <title1 (default = Havbris)>, <title2 (default = Norkyst)>, <frame>, <start_time>, <kwargs (optional)>')
        for i in range (12):
            print(sys.argv[i])
        file_path_1 = sys.argv[2]
        file_path_2 = sys.argv[3]
        file_path_3 = sys.argv[4]
        variable1 = sys.argv[5]
        variable2 = sys.argv[6]
        dir = sys.argv[7]
        model_name = sys.argv[8]
        title1 = sys.argv[9]
        title2 = sys.argv[10]
        frame = int(sys.argv[11])
        start_time = int(sys.argv[12])

        kwargs = {}
        for arg in sys.argv[13:]:
            key, value = arg.split('=')
            kwargs[key] = float(value)

        animation_compare(file_path_1, file_path_2, file_path_3, variable1, variable2, dir, model_name, title1, title2, frame, start_time, **kwargs)

