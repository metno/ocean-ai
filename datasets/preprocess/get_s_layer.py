import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
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

def get_s_layer(file, depth, time=0, output=None, plot=False):
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
    diff = abs(abs(ds['z_rho'])-depth).fillna(0)
    index = diff.argmin(dim = 's_rho').rename(f'{depth}m-s-layer-index')
    index = index.where(index != 0)
    if output is not None:
        index.to_netcdf(output)
    if plot:
        ax = sns.heatmap(np.array(index)[::-1,::-1], cbar_kws={'label': 'Index'}, vmin=30, vmax=40)
        plt.savefig('o.png')
    return index
      

if __name__ == '__main__':
    file = f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-20240601.nc'
    get_s_layer(file, 10, 0, plot=True)
