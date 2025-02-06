import numpy as np
import scipy.interpolate
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

#-----------------------------------------------------------------
# These functions are either a copy of or inspired by
# anemoi-utils/anemoi-utils/utils.py

def mesh(lat, lon, increment):
    """ TODO"""
    lat = np.arange(lat.min(), lat.max(), increment)
    lon = np.arange(lon.min(), lon.max(), increment)
    lat_grid, lon_grid = np.meshgrid(lat, lon)
    return lat_grid.T, lon_grid.T

def interpolate(data, lat, lon, increment):
    """ TODO"""
    era_lat_gridded, era_lon_gridded = mesh(lat, lon, increment)

    # Interpolate irregular ERA grid to regular lat/lon grid
    icoords = np.asarray([lon, lat], dtype=np.float32).T
    ocoords = np.asarray([era_lon_gridded.flatten(), era_lat_gridded.flatten()], dtype=np.float32).T

    interpolator = scipy.interpolate.NearestNDInterpolator(icoords, data) # input coordinates
    q = interpolator(ocoords)  # output coordinates
    q = q.reshape(era_lat_gridded.shape)
    return q

def panel_config_auto(ens_size, extra_panels):
    """Configure panel orientation, given
    number of ensemble members."""
    ens_size = 1 if ens_size is None else ens_size
    n_panels = ens_size
    n_panels += extra_panels

    conf_map = [None,
                (1,1), (1,2), (2,2), (2,2),
                (2,3), (2,3), (2,4), (2,4),
                (3,3), (3,4), (3,4), (3,4),
                (4,4), (4,4), (4,4), (4,4),
               ]
    panel_limit = len(conf_map) - 1

    if n_panels > panel_limit:
        print(f"Panel limit reached, continuing with {panel_limit} panels")
        n_panels = panel_limit
        ens_size = panel_limit - extra_panels

    n = conf_map[n_panels]
    return n, ens_size

def plot(ax, data, lat_grid, lon_grid, **kwargs):
    """Plot data using pcolormesh on redefined ax"""
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN, edgecolor='black')
    im = ax.pcolormesh(lon_grid, lat_grid, data, **kwargs)
    #im = ax.contourf(lon_grid, lat_grid, data)
    return im

#-----------------------------------------------------------------

def plot_landmask(ax,color='black',file='/lustre/storeB/project/fou/hi/foccus/ina/ocean-ai/plot/surface_mask_contour_paths.npy'):
    # See /lustre/storeB/project/fou/hi/foccus/ina/ocean-ai/plot/save_surface_contour.py
    contour_loaded = np.load(file, allow_pickle=True)

    # Plot each contour path
    for vertices in contour_loaded:
        ax.plot(vertices[:, 0], vertices[:, 1], color=color)

    return

def simple_mesh_plot(var_grid,lat_grid,lon_grid,time,var_name,vmin=-4,vmax=26):
    """Simple pcolormesh plot"""
    # TODO: add options for **kwargs
    kwargs = {}
    kwargs['shading'] = 'auto' ##se også på norm
    kwargs['cmap'] = 'viridis'
    kwargs['vmin'] = vmin
    kwargs['vmax'] = vmax 

    fig, ax = plt.subplots(figsize=(8, 6),squeeze=False, subplot_kw={'projection': ccrs.PlateCarree()})
    ax1=ax[0,0]
    ax1.add_feature(cfeature.BORDERS, linestyle=':') # the coastline feature is not accurate enough
    
    heatmap = ax1.pcolormesh(lon_grid, lat_grid, var_grid, **kwargs)
    # TODO: idea to use contour?
    #ax1.contourf(lon_grid, lat_grid, var_grid)
    
    # Plot the land-sea mask
    plot_landmask(ax1)

    # TODO improve this cbar and fig size etc
    cbar = fig.colorbar(heatmap, ax=ax1, orientation='vertical')
    cbar.set_label(var_name)
    ax1.set_title(f'Time step: {time}')

    ax1.set_xlim([lon_grid.min(), lon_grid.max()])
    ax1.set_ylim([lat_grid.min(), lat_grid.max()])

    return fig, ax1, heatmap

def update_anim(frame,ax,heatmap,var,time):
    """TODO"""
    heatmap.set_array(var[frame].ravel())
    ax.set_title(f'Time step: {time[frame]}')

def plot_h_contours(ax, levels=20, file='/lustre/storeB/project/fou/hi/foccus/mateuszm/ocean-ai/datasets/h_for_contour.nc', lon_min=None, lon_max=None, lat_min=None, lat_max=None):
    from dataloader import open_dataset
    h = open_dataset(file, lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max).dataset.isel(time=0)
    ax.contour(h.longitude, h.latitude, h.h, levels=levels, colors='dimgray', linestyles='dashed', linewidths=1, alpha=0.8)

def plot_variable_field(ds, var, ax=None, time=None, outfile=None, cmap=None, fig=None):
    """
    Simple plot of the field of a variable. 
    Currently doing scatterplot, but may be updated to pcolormesh when we have 2D. 

    Args:
        ds  [dataarray] :   
        var [str]       :   
        ax  []          :   
        time    [int]   :   
        outfile [str]   :   
        cmap    [str]   :   

    """
    print(f'Plotting variable {var}')
    if ax is None:
        fig = plt.figure(dpi=150)
        ax = fig.add_subplot(111)
    
    if time is not None:
        ds = ds.isel(time=time)

    if 'longitude' and 'latitude' in ds.variables:
        lon_name, lat_name = 'longitude', 'latitude'
    elif 'lon' and 'lat' in ds.variables:
        lon_name, lat_name = 'lon', 'lat'

    im = ax.scatter(ds[lon_name], ds[lat_name], c=ds[var], s=3, cmap=cmap)
    ax.set_ylim(np.min(ds[lat_name]), np.max(ds[lat_name]))
    ax.set_xlim(np.min(ds[lon_name]), np.max(ds[lon_name]))
    ax.set_facecolor('xkcd:beige')
    ax.set_title(var)
    ax.grid(ls='--', color='lightgray')
    plot_landmask(ax)
    plot_h_contours(ax, lon_min=np.min(ds[lon_name]), lon_max=np.max(ds[lon_name]), lat_min=np.min(ds[lat_name]), lat_max=np.max(ds[lat_name]), levels=15)
    if fig is not None:
        cax = fig.add_axes([ax.get_position().x1+0.015, ax.get_position().y0, 0.025, ax.get_position().height])
        cbar = fig.colorbar(im, ax=ax, cax=cax)
    if outfile is not None:
        plt.savefig(outfile+'.png')
    
    return ax

def plot_all_available_vars(ds, time=None, outfile=None, cmap=None):
    """
    Plot all variables
    """
    exclude = ['forecast_reference_time', 'time', 'location', 'latitude', 'longitude']
    plotting_vars = []
    for var in ds.variables:
        if var not in exclude:
            plotting_vars.append(var)
    
    cols = 3
    rows = int(np.ceil(len(plotting_vars)/cols))
    fig, axs = plt.subplots(cols, rows, figsize=(10*cols, 10*rows))
    i = 0
    for col in range(cols):
        for row in range(rows):
            if i < len(plotting_vars):
                plot_variable_field(ds=ds, var=plotting_vars[i], ax=axs[col, row], time=time, fig=fig, cmap=cmap)
                i+=1
    if outfile is not None:
        plt.savefig(outfile+'.png')

def compare_variable(ds1, ds2, var1, var2, outfile=None, time=None):
    fig, axs = plt.subplots(1,3)
    plot_variable_field(ds1, var1, ax=axs[0], time=time)
    plot_variable_field(ds2, var2, ax=axs[1])
    if outfile is not None:
        plt.savefig(outfile+'.png')
