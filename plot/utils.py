import numpy as np
import scipy.interpolate
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

def mesh(lat, lon, increment):
    lat = np.arange(lat.min(), lat.max(), increment)
    lon = np.arange(lon.min(), lon.max(), increment)
    lat_grid, lon_grid = np.meshgrid(lat, lon)
    return lat_grid.T, lon_grid.T

def interpolate(data, lat, lon, increment):
    """ """
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
def subset_variable(var,lat,lon,lat_min,lat_max,lon_min,lon_max):
    """
    Subsets the dataset to the specified longitude and latitude range,
    and returns new arrays of the variable, longitude and latitude.
    
    Parameters:
    var (np.array): The input variable.
    lat (np.array): The input latitude.
    lon (np.array): The input longitude.
    lat_min (float): Minimum latitude.
    lat_max (float): Maximum latitude.
    lon_min (float): Minimum longitude.
    lon_max (float): Maximum longitude.

    Returns:
    ...TODO add
    """

    # Create a mask for the bounding box
    lon_mask = (lon >= lon_min) & (lon <= lon_max)
    lat_mask = (lat >= lat_min) & (lat <= lat_max)
    
    # Combine masks
    combined_mask = lon_mask & lat_mask
    
    # Apply the mask to filter the data
    filtered_lon = lon[combined_mask]
    filtered_lat = lat[combined_mask]
    filtered_var = var[:, combined_mask]

    return filtered_var,filtered_lat,filtered_lon

def simple_mesh_plot(var_grid,lat_grid,lon_grid,time,var_name):
    """Simple pcolormesh plot"""
    # TODO: add options for **kwargs
    kwargs = {}
    kwargs['shading'] = 'auto' #kwargs['vmin'] = vmin; kwargs['vmax'] = vmax #se også på norm
    kwargs['cmap'] = 'viridis'

    fig, ax = plt.subplots(figsize=(8, 6),squeeze=False, subplot_kw={'projection': ccrs.PlateCarree()})
    ax1=ax[0,0]
    # TODO: get land seamask and plot that as coastline
    ax1.add_feature(cfeature.COASTLINE)
    ax1.add_feature(cfeature.BORDERS, linestyle=':')
    ax1.add_feature(cfeature.LAND, edgecolor='black')
    
    heatmap = ax1.pcolormesh(lon_grid, lat_grid, var_grid, **kwargs)
    # TODO: idea to use contour?
    #ax1.contourf(lon_grid, lat_grid, var_grid)

    # TODO improve this cbar and fig size etc
    #cbar = fig.colorbar(heatmap, ax=ax1, orientation='vertical')
    #cbar.set_label(var_name)
    ax1.set_title(f'Time step: {time}')

    return fig, ax1, heatmap#, cbar

def update_anim(frame,ax,heatmap,var,time):
    heatmap.set_array(var[frame].ravel())
    ax.set_title(f'Time step: {time[frame]}')
