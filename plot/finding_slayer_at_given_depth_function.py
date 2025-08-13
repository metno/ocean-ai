import xarray as xr
import matplotlib.pyplot as plt 
import numpy as np 
import seaborn as sns

def transformation(ds_name):
    #Define necessary variables used for the transformation from s_layer to depth
    hc = ds_name["hc"] #Critical depth for stretching
    cs_r = ds_name["Cs_r"] #stretching curve at rho points
    zeta = ds_name["zeta"] #.fillna(0) #free-surface 
    H = ds_name["h"] #bathymetry at rho-points (depth)
    #Vtransform = ds_name["Vtransform"] Not in this dataset
    s_rho = ds_name["s_rho"] #range 1,40. 40 is surface layer

    #Transformation process
    Z_0_rho = (hc * s_rho + cs_r * H) / (hc + H)
    z_rho = zeta + (zeta + H) * Z_0_rho

    ds_name.coords["z_rho"] = z_rho.transpose() #Corrects the dimensions
    return z_rho

def add_coordinate(ds_name):
    ds_name["z_rho"] = transformation(ds_name) #adds z_rho as a coordinate to the dataset
    return ds_name

def plot_the_2m_layer_grid(ds_name, meter): #plotting the matrix consisting of s-layer index
    add_coordinate(ds_name = ds_name)
    transformation(ds_name=ds_name)
    z_rho = ds_name["z_rho"]
    z_rho_pos = abs(ds_name["z_rho"])
    diff = abs(z_rho_pos-meter) #meter is the depth you wish to find the corresponding s-layers for, for an example 2m, 10m etc. 
    diff = diff.fillna(0)
    index = diff.argmin(dim = "s_rho")
    close_to_2m_val = z_rho.isel(s_rho=index)
    #zero = nan in plot
    index = index.where(index != 0)
    #ax = sns.heatmap(np.array(index), vmin=25, cbar_kws={'label': 'Index'})
    #ax.set_title(title)
    return f'this is the selected {index}', close_to_2m_val

def plot_the_2m_layer(ds_name, title, meter, **kwargs):
    #kwargs can be used if one wants to add vmin and vmax to the plots or other potential arguments 
    add_coordinate(ds_name = ds_name)
    transformation(ds_name=ds_name)
    z_rho = ds_name["z_rho"]
    z_rho_pos = abs(ds_name["z_rho"])
    diff = abs(z_rho_pos-meter) #the meter you wish to find the corresponding s-layer for 
    diff = diff.fillna(0)
    index = diff.argmin(dim = "s_rho")
    close_to_m_val = z_rho.isel(s_rho=index)
    #zero = nan in plot
    index = index.where(index != 0)
    ax = sns.heatmap(np.array(index)[::-1,::-1], cbar_kws={'label': 'Index'}, **kwargs)
    ax.set_title(title)
    plt.show()
    return index, close_to_m_val, ax

def get_s_layer(file, depth, time=0, output=None):
    """
    Function to find which model s-layer is closest to a given depth in meters.

    Args:
        file    [str]               :   ROMS model file
        depth   [int]               :   Depth in meters of interest
        time    [int, str or list]  :   Time index of dataset, or list of times to slice over. If time='all' will select all times. 
        output  [str]               :   Name of output file

    Returns:
        index   [DataArray]   :   A DataArray of indexes corresponding to the s-layer which is closest to the given depth at all grid points.         
    """
    ds = xr.open_dataset(file)
    if time == 'all':
        pass
    elif type(time) is int:
        ds = ds.isel(time=time)
    elif type(time) is list and len(time) == 2:
        ds = ds.isel(time=slice(time[0], time[1]))

    add_coordinate(ds)
    diff = abs(abs(ds['z_rho']-depth)).fillna(0)
    index = diff.argmin(dim = 's_rho').rename(f'{depth}m-s-layer-index')
    
    if output is not None:
        index.to_netcdf(output)

    return index
      

if __name__ == '__main__':
    #example on how to run the code:
    file = f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-20240601.nc' #netcdf4 file to use 
    #ds = xr.open_dataset(file1).sel(time = '2024-06-01T07:00:00.000000000') #this is the dataset and the ds_name in the function
    #add_coordinate(ds_name=ds)
    #index, m_value, plot = plot_the_2m_layer(ds_name=ds, title = "Example plot", meter=10)
    get_s_layer(file, 2, [0,3])
    #then use index, m_value etc. as you need later in your code.
    #use _, in case you dont need all returned values.