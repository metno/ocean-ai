#Importing necessary packages
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 
import cartopy 
import cmocean 
import cartopy.crs as ccrs 
import cartopy.feature as cfeature

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
    arg[1] : ds - The dataset you wish to calculate the mean for. This one works for the Inference results (Havbris). 
    arg[2] : avg_time - The period you wish to calculate average for. Please enter a value such as 'D' for one day, '2D' for two days, '1W' for one week etc. 

    Outputs:
    The mean velocity for U and V. 
    """
    mean_u_vel = ds['u_eastward'].resample(time = 'D').mean(dim = 'time')
    mean_v_vel = ds['v_northward'].resample(time = 'D').mean(dim = 'time')
    return mean_u_vel, mean_v_vel


#Calculate f/h contours

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


#Plotting

#Norkyst
def fh_norkyst(area, fh, u_vel, v_vel, title, step = 5, min_l = -0.5e-5, max_l = 1.44e-5):

    #calculate means
    u_vel, v_vel = mean_norkyst(area)
    #calculate f/h contours
    fh = fh_norkyst(area)

    fig, ax = plt.subplots(figsize = (10,12), subplot_kw={'projection' : ccrs.NorthPolarStereo()})
    step = step
    min_l = min_l
    max_l = max_l
    custom = np.linspace(min_l, max_l, 20)
    im = ax.contour(area.lon.values, area.lat.values, fh[:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
    im_fill = ax.contourf(area.lon.values, area.lat.values, fh[:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
    ax.quiver(area.lon.values[::step, ::step], area.lat.values[::step, ::step], u_vel[0,-1,:,:].values[::step, ::step], v_vel[0,-1,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 30)
    cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
    cbar = fig.colorbar(im_fill, ax=ax, cax = cax, extend = 'both')
    cbar.ax.set_title(r'$\frac{f}{h}$')
    gl = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
    gl.xlabels_top = False 
    gl.ylabels_right = False 
    ax.set_title(f'{title}')
    ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')

#Inference results
def fh_inference(area, title, step = 5, min_l = -0.5e-5, max_l = 1.44e-5, compare_norkyst_area = None, title2 = None):

    if compare_norkyst_area is None:
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
        im = ax.contour(area.lon.values[0,:,:], area.lat[0,:,:].values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
        im_fill = ax.contourf(area.lon[0,:,:].values, area.lat[0,:,:].values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
        ax.quiver(area.lon[0,:,:].values[::step, ::step], area.lat[0,:,:].values[::step, ::step], u_vel[0,:,:].values[::step, ::step], v_vel[0,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 20)
        cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
        cbar = fig.colorbar(im_fill, ax=ax, cax = cax, extend = 'both')
        cbar.ax.set_title(r'$\frac{f}{h}$')
        gl = ax.gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
        gl.xlabels_top = False 
        gl.ylabels_right = False 
        ax.set_title(f'{title}')
        ax.add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')
        plt.show()
    else: 
        #calculate means
        u_vel, v_vel = mean_inference(area)
        #u_vel_nor, v_vel_nor = mean_norkyst(compare_norkyst_area)
        #calculate f/h contours
        fh = fh_values_inference(area)
        fh_nor = fh_norkyst(compare_norkyst_area)

        #plot
        fig, ax = plt.subplots(1,2, figsize = (10,12), subplot_kw={'projection' : ccrs.NorthPolarStereo()})
        step = step
        min_l = min_l
        max_l = max_l
        custom = np.linspace(min_l, max_l, 20)

        #Inference
        im1 = ax[0].contour(area.lon.values, area.lat.values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
        im_fill1 = ax[0].contourf(area.lon.values, area.lat.values, fh[0,:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
        ax[0].quiver(area.lon.values[::step, ::step], area.lat.values[::step, ::step], u_vel[1,:,:].values[::step, ::step], v_vel[1,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 20)
        cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
        cbar1 = fig.colorbar(im_fill1, ax=ax[0], cax = cax, extend = 'both')
        cbar1.ax[0].set_title(r'$\frac{f}{h}$')
        gl1 = ax[0].gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
        gl1.xlabels_top = False 
        gl1.ylabels_right = False 
        ax[0].set_title(f'Inference {title}')
        ax[0].add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')

        #Norkyst
        im2 = ax[1].contour(area.lon.values, area.lat.values, fh_nor[:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 2, color = 'black')
        im_fill2 = ax[1].contourf(area.lon.values, area.lat.values, fh_nor[:,:], levels = custom, transform = ccrs.PlateCarree(), zorder = 1, cmap = cmocean.cm.topo)
        ax[1].quiver(area.lon.values[::step, ::step], area.lat.values[::step, ::step], u_vel_nor[0,-1,:,:].values[::step, ::step], v_vel_nor[0,-1,:,:].values[::step, ::step], transform = ccrs.PlateCarree(), color = 'black', alpha = 0.6, scale = 30)
        cax = fig.add_axes([ax.get_position().x1+0.025, ax.get_position().y0, 0.025, ax.get_position().height])
        cbar2 = fig.colorbar(im_fill2, ax=ax[1], cax = cax, extend = 'both')
        cbar2.ax[1].set_title(r'$\frac{f}{h}$')
        gl2 = ax[1].gridlines(crs = ccrs.PlateCarree(), draw_labels = True, linewidth = 1, color = 'black', alpha = 0.1, linestyle = '--')
        gl2.xlabels_top = False 
        gl2.ylabels_right = False 
        ax[1].set_title(f'{title2}')
        ax[1].add_feature(cartopy.feature.LAND, zorder = 1, edgecolor = 'black')

        plt.show()