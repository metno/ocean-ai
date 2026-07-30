#Importing necessary packages
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 
import cartopy 
import cmocean 
import cartopy.crs as ccrs 
import cartopy.feature as cfeature

########################### Calculating the mean velocities from Norkyst or Havbris ################################

#Norkyst
def mean_norkyst(ds):
    """
    Description:
    The function calculates the mean velocity for U and V ocean currents for a given period of time.  

    Inputs:
    arg[1] : ds - The dataset you wish to calculate the mean for. This one works for Norkyst. 
    arg[2] : avg_time - The period you wish to calculate average for. Please enter a value such as 'D' for one day, '2D' for two days, '1W' for one week etc. 

    Outputs:
    The mean velocity for U and V. 
    """

    mean_u_vel = ds['u_eastward'].resample(time = 'D').mean(dim = 'time')
    mean_v_vel = ds['v_northward'].resample(time = 'D').mean(dim = 'time')
    return mean_u_vel, mean_v_vel

#Inference results
def mean_inference(ds):
    """
    Description:
    The function calculates the mean velocity for U and V ocean currents for a given period of time.  

    Inputs:
    arg[1] : ds - The dataset you wish to calculate the mean for. This one works for the Inference results as long as opened with the dataloader package from Mateusz (or else variable names do not match)
    arg[2] : avg_time - The period you wish to calculate average for. Please enter a value such as 'D' for one day, '2D' for two days, '1W' for one week etc. 

    Outputs:
    The mean velocity for U and V. 
    """
    mean_u_vel = ds['u_eastward'].resample(time = 'D').mean(dim = 'time')
    mean_v_vel = ds['v_northward'].resample(time = 'D').mean(dim = 'time')
    return mean_u_vel, mean_v_vel


#Calculate f/h contours########################### Calculating the f/h contours from Norkyst or Havbris ################################
#Norkyst
def fh_norkyst_value(ds):
    """
    Description:
    The function calculates the f/h values. This function is meant for Norkyst, because it lacks f as a variable in the dataset and has to be calculated manually.

    Inputs: 
    arg[1] : ds - The dataset you wish to calculate the f/h values for. 

    Outputs:
    Returns the values for f/h. 
    """
    h = ds.h
    omega = 7.2921e-5
    lat_nor = ds.lat
    lat_nor_rad = np.deg2rad(lat_nor)
    f_nor = 2 * omega * np.sin(lat_nor_rad)
    f_h = f_nor/h
    return f_h 

#Inference results
def fh_values_inference(ds):
    """
    Description:
    The function calculates the f/h values. This function is meant for Inference results (Havbris), because the dataset already contains the values for f & h.

    Inputs: 
    arg[1] : ds - The dataset you wish to calculate the f/h values for. 

    Outputs:
    Returns the values for f/h. 
    """
    h = ds.h 
    f = ds.f
    f_h = f.values / h.values
    print(f'f_h has dimensions: {f_h.shape}')
    return f_h 


########################### Plotting functions for Norkyst or Havbris ################################

def fh_norkyst(area, title, save_path, step = 5, min_l = -0.5e-5, max_l = 1.44e-5):

    """
    Definition:
    A function for plotting the f/h contours for the Norkyst files. 

    Arguments:
    arg[1] - Area (dataset) - named area because the chosen area to plot must be cut out before passing the dataset. 
    arg[2] - title (str) - title of the Figure
    arg[3] - Save_path (str) - path to save the Figure. Please enter full path.

    Returns:
    A plot saved as a png Figure.
    """

    #calculate means
    u_vel, v_vel = mean_norkyst(area)
    print(f'shape of uvel: {u_vel.shape}, shape of vvel: {v_vel.shape}')
    #calculate f/h contours
    fh = fh_norkyst_value(area)

    fig, ax = plt.subplots(figsize = (10,12), subplot_kw={'projection' : ccrs.NorthPolarStereo()})
    step = step
    min_l = min_l
    max_l = max_l
    custom = np.linspace(min_l, max_l, 20)
    im = ax.contour(area.lon.values, area.lat.values, fh[:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
    im_fill = ax.contourf(area.lon.values, area.lat.values, fh[:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
    ax.quiver(area.lon.values[::step, ::step], area.lat.values[::step, ::step], u_vel[0,:,:].values[::step, ::step], v_vel[0,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 30)
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im_fill, ax=ax, cax = cax, extend = 'both')
    cbar.ax.set_title(r'$\frac{f}{h}$')
    gl = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
    gl.xlabels_top = False 
    gl.ylabels_right = False 
    ax.set_title(f'{title}')
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')
    fig.savefig(save_path)

def fh_inference(area, title, save_path, step = 5, min_l = -0.5e-5, max_l = 1.44e-5):

    """
    Definition:
    A function for plotting the f/h contours for the Havbris files. 

    Arguments:
    arg[1] - Area (dataset) - named area because the chosen area to plot must be cut out before passing the dataset. 
    arg[2] - title (str) - title of the Figure
    arg[3] - Save_path (str) - path to save the Figure. Please enter full path.

    Returns:
    A plot saved as a png Figure.
    """

    #calculate means
    u_vel, v_vel = mean_inference(area)
    print(f'Shape U: {u_vel.shape}. Shape V ; {v_vel.shape}.')
    #calculate f/h contours
    fh = fh_values_inference(area)
    #plot
    fig, ax = plt.subplots(figsize = (10,12), subplot_kw={'projection' : ccrs.NorthPolarStereo()})
    step = step
    min_l = min_l
    max_l = max_l
    custom = np.linspace(min_l, max_l, 20)
    im = ax.contour(area.lon.values[:,:], area.lat[:,:].values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
    im_fill = ax.contourf(area.lon[:,:].values, area.lat[:,:].values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
    ax.quiver(area.lon[:,:].values[::step, ::step], area.lat[:,:].values[::step, ::step], u_vel[0,:,:].values[::step, ::step], v_vel[0,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 20)
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im_fill, ax=ax, cax = cax, extend = 'both')
    cbar.ax.set_title(r'$\frac{f}{h}$')
    gl = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
    gl.xlabels_top = False 
    gl.ylabels_right = False 
    ax.set_title(f'{title}')
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')
    fig.savefig(save_path)